#
#  Copyright 2023 The FATE Authors. All Rights Reserved.
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

import torch


def initialize_param(coef_len, **kwargs):
    param_len = coef_len
    method = kwargs["method"]
    fit_intercept = kwargs["fit_intercept"]
    if fit_intercept:
        param_len = param_len + 1
    if method == 'zeros':
        return torch.zeros((param_len, 1), requires_grad=True)
    elif method == 'ones':
        return torch.ones((param_len, 1), requires_grad=True)
    elif method == 'consts':
        return torch.full((param_len, 1), float(kwargs["fill_val"]), requires_grad=True)
    elif method == 'random':
        return torch.randn((param_len, 1), requires_grad=True)
    else:
        raise NotImplementedError(f"Unknown initialization method: {method}")