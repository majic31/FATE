#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import logging

import torch

from fate.arch import Context
from fate.arch.dataframe import DataLoader
from fate.ml.abc.module import HeteroModule
from fate.ml.utils._model_param import (
    deserialize_param,
    initialize_param,
    serialize_param,
)
from fate.ml.utils._optimizer import LRScheduler, Optimizer

logger = logging.getLogger(__name__)


class CoordinatedPoissonModuleHost(HeteroModule):
    def __init__(self, epochs, batch_size, optimizer_param, learning_rate_param, init_param):
        self.epochs = epochs
        self.optimizer_param = optimizer_param
        self.learning_rate_param = learning_rate_param
        self.batch_size = batch_size
        self.init_param = init_param or {}
        self.init_param["fit_intercept"] = False

        self.estimator = None

    def set_batch_size(self, batch_size):
        self.batch_size = batch_size
        self.estimator.batch_size = batch_size

    def set_epochs(self, epochs):
        self.epochs = epochs
        self.estimator.epochs = epochs

    def fit(self, ctx: Context, train_data, validate_data=None) -> None:
        encryptor = ctx.arbiter("encryptor").get()
        if self.estimator is None:
            optimizer = Optimizer(
                self.optimizer_param["method"],
                self.optimizer_param["penalty"],
                self.optimizer_param["alpha"],
                self.optimizer_param["optimizer_params"],
            )
            lr_scheduler = LRScheduler(
                self.learning_rate_param["method"], self.learning_rate_param["scheduler_params"]
            )
            estimator = CoordinatedPoissonEstimatorHost(
                epochs=self.epochs,
                batch_size=self.batch_size,
                optimizer=optimizer,
                learning_rate_scheduler=lr_scheduler,
                init_param=self.init_param,
            )
            self.estimator = estimator

        self.estimator.fit_model(ctx, encryptor, train_data, validate_data)

    def predict(self, ctx, test_data):
        self.estimator.predict(ctx, test_data)

    def get_model(self):
        return {
            "data": {"estimator": self.estimator.get_model()},
            "meta": {
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "learning_rate_param": self.learning_rate_param,
                "init_param": self.init_param,
                "optimizer_param": self.optimizer_param,
            },
        }

    @classmethod
    def from_model(cls, model) -> "CoordinatedPoissonModuleHost":
        poisson_model = CoordinatedPoissonModuleHost(
            optimizer_param=model["meta"]["optimizer_param"],
            learning_rate_param=model["meta"]["learning_rate_param"],
            epochs=model["meta"]["epochs"],
            batch_size=model["meta"]["batch_size"],
            init_param=model["meta"]["init_param"],
        )
        estimator = CoordinatedPoissonEstimatorHost(
            epochs=model["meta"]["epochs"],
            batch_size=model["meta"]["batch_size"],
            init_param=model["meta"]["init_param"],
        )
        estimator.restore(model["data"]["estimator"])
        poisson_model.estimator = estimator

        return poisson_model


class CoordinatedPoissonEstimatorHost(HeteroModule):
    def __init__(self, epochs=None, batch_size=None, optimizer=None, learning_rate_scheduler=None, init_param=None):
        self.epochs = epochs
        self.optimizer = optimizer
        self.lr_scheduler = learning_rate_scheduler
        self.batch_size = batch_size
        self.init_param = init_param

        self.w = None
        self.start_epoch = 0
        self.end_epoch = -1
        self.is_converged = False

    def centralized_compute_gradient(self, batch_ctx, encryptor, w, X):
        h = X.shape[0]
        Xw_h = torch.matmul(X, w.detach())
        mu_h = torch.exp(Xw_h)
        batch_ctx.guest.put("mu_h", encryptor.encrypt_tensor(mu_h))

        batch_ctx.guest.put("Xw_h", encryptor.encrypt_tensor(Xw_h))
        loss_norm = self.optimizer.loss_norm(w)
        if loss_norm is not None:
            batch_ctx.guest.put("h_loss", encryptor.encrypt_tensor(loss_norm))
        else:
            batch_ctx.guest.put("h_loss", loss_norm)

        d = batch_ctx.guest.get("d")
        g = 1 / h * torch.matmul(X.T, d)
        return g

    def fit_model(self, ctx: Context, encryptor, train_data, validate_data=None) -> None:
        batch_loader = DataLoader(train_data, ctx=ctx, batch_size=self.batch_size, mode="hetero", role="host")

        coef_count = train_data.shape[1]
        w = self.w
        if self.w is None:
            w = initialize_param(coef_count, **self.init_param)
            self.optimizer.init_optimizer(model_parameter_length=w.size()[0])
            self.lr_scheduler.init_scheduler(optimizer=self.optimizer.optimizer)
        # if self.end_epoch >= 0:
        #    self.start_epoch = self.end_epoch + 1
        for i, iter_ctx in ctx.on_iterations.ctxs_range(self.epochs):
            self.optimizer.set_iters(i)
            logger.info(f"self.optimizer set epoch {i}")
            for batch_ctx, batch_data in iter_ctx.on_batches.ctxs_zip(batch_loader):
                X = batch_data.x
                g = self.centralized_compute_gradient(batch_ctx, encryptor, w, X)
                g = self.optimizer.add_regular_to_grad(g, w, False)
                batch_ctx.arbiter.put("g_enc", g)
                g = batch_ctx.arbiter.get("g")

                w = self.optimizer.update_weights(w, g, False, self.lr_scheduler.lr)
                logger.info(f"w={w}")
            self.is_converged = iter_ctx.arbiter("converge_flag").get()
            if self.is_converged:
                self.end_epoch = i
                break
            if i < self.epochs - 1:
                self.lr_scheduler.step()
        if not self.is_converged:
            self.end_epoch = self.epochs
        self.w = w
        logger.debug(f"Finish training at {self.end_epoch}th epoch.")

    def predict(self, ctx, test_data):
        X = test_data.values.as_tensor()
        output = torch.matmul(X, self.w)
        ctx.guest.put("h_pred", output)

    def get_model(self):
        param = serialize_param(self.w, False)
        return {
            "param": param,
            "optimizer": self.optimizer.state_dict(),
            "lr_scheduler": self.lr_scheduler.state_dict(),
            "end_epoch": self.end_epoch,
            "is_converged": self.is_converged,
        }

    def restore(self, model):
        # self.w = torch.tensor(model["w"])
        self.w = deserialize_param(model["param"], False)
        self.optimizer = Optimizer()
        self.lr_scheduler = LRScheduler()
        self.optimizer.load_state_dict(model["optimizer"])
        self.lr_scheduler.load_state_dict(model["lr_scheduler"], self.optimizer.optimizer)
        self.end_epoch = model["end_epoch"]
        self.is_converged = model["is_converged"]
