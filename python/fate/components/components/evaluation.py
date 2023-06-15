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
from fate.components import (
    ARBITER,
    GUEST,
    HOST,
    ClassificationMetrics,
    DatasetArtifact,
    Input,
    Output,
    Role,
    cpn,
)
import numpy as np
import pandas as pd
from fate.ml.evaluation import classification as classi
from fate.ml.evaluation import regression as reg
from fate.ml.evaluation.metric_base import Metric, MetricEnsemble
from fate.components.params import string_choice
from typing import Dict
import inspect
import logging


logger = logging.getLogger(__name__)


def get_metric_names(modules):
    result = {}

    for module in modules:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if hasattr(obj, 'metric_name'):
                    metric_name = getattr(obj, 'metric_name')
                    if metric_name is not None:
                        result[metric_name] = obj

    return result


def get_binary_metrics():

    binary_ensembles = MetricEnsemble()
    binary_ensembles.add_metric(classi.AUC()).add_metric(classi.KS()).add_metric(classi.ConfusionMatrix())
    binary_ensembles.add_metric(classi.Gain()).add_metric(classi.Lift())
    binary_ensembles.add_metric(classi.BiClassPrecisionTable()).add_metric(classi.BiClassRecallTable())
    binary_ensembles.add_metric(classi.BiClassAccuracyTable()).add_metric(classi.FScoreTable())
    return binary_ensembles


def get_multi_metrics():
    
    multi_ensembles = MetricEnsemble()
    multi_ensembles.add_metric(classi.MultiAccuracy()).add_metric(classi.MultiPrecision).add_metric(classi.MultiRecall())
    
    return multi_ensembles


def get_regression_metrics():
    
    regression_ensembles = MetricEnsemble()
    regression_ensembles.add(reg.RMSE()).add(reg.MAE()).add(reg.MSE()).add(reg.R2Score())
    return regression_ensembles


def get_special_metrics():
    # metrics that need special input format like PSI
    ensembles = MetricEnsemble()
    ensembles.add_metric(classi.PSI())
    return ensembles


def get_specified_metrics(metric_names: list):
    ensembles = MetricEnsemble()
    available_metrics = get_metric_names([classi, reg])
    for metric_name in metric_names:
        if metric_name in available_metrics:
            ensembles.add_metric(get_metric_names([classi, reg])[metric_name]())
        else:
            raise ValueError(f"metric {metric_name} is not supported yet, supported metrics are \n {list(available_metrics.keys())}")
    return ensembles


def split_dataframe_by_type(input_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:

    if 'type' in input_df.columns:
        return {dataset_type: input_df[input_df['type'] == dataset_type] for dataset_type in input_df['type'].unique()}
    else:
        return {'origin': input_df}


@cpn.component(roles=[GUEST, HOST, ARBITER])
@cpn.artifact("input_data", type=Input[DatasetArtifact], roles=[GUEST, HOST, ARBITER])
@cpn.parameter("default_eval_metrics", type=string_choice(choice=['binary', 'multi', 'regression']), default="binary", optional=True)
@cpn.parameter("metrics", type=list, default=None, optional=True)
@cpn.artifact("output_metric", type=Output[ClassificationMetrics], roles=[GUEST, HOST, ARBITER])
def evaluation(ctx, role: Role, input_data, default_eval_metrics, metrics, output_metric):

    if role.is_arbiter:
        return
    else:
        if metrics is not None:
            metrics_ensemble = get_specified_metrics(metrics)
        else:
            if default_eval_metrics == "binary":
                metrics_ensemble = get_binary_metrics()
            elif default_eval_metrics == "multi":
                metrics_ensemble = get_multi_metrics()
            elif default_eval_metrics == "regression":
                metrics_ensemble = get_regression_metrics()

        rs_dict = evaluate(ctx, input_data, metrics_ensemble, output_metric)

    logger.info('eval result: {}'.format(rs_dict))


def evaluate(ctx, input_data, metrics, output_metric):

    data = ctx.reader(input_data).read_dataframe().data.as_pd_df()
    split_dict = split_dataframe_by_type(data)
    rs_dict = {}

    for name, df in split_dict.items():

        y_true = df.label.values.flatten()
        y_pred = np.array( df.predict_prob.values.tolist()).flatten()
        rs = metrics(predict=y_pred, label=y_true)
        rs_dict[name] = rs

    return rs_dict


if __name__ == '__main__':
    rs = get_metric_names([classi, reg])
