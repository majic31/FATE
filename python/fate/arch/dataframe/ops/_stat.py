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
import functools

import numpy as np
import pandas as pd
import torch
from .._dataframe import DataFrame
from ..manager import DataManager


def min(df: "DataFrame"):
    data_manager = df.data_manager
    operable_blocks = data_manager.infer_operable_blocks()

    def _mapper(blocks, op_bids):
        ret = []
        for bid in op_bids:
            if isinstance(blocks[bid], torch.Tensor):
                ret.append(blocks[bid].min(axis=0).values)
            else:
                ret.append(blocks[bid].min(axis=0))

        return ret

    def _reducer(blocks1, blocks2):
        ret = []
        for block1, block2 in zip(blocks1, blocks2):
            if isinstance(block1, torch.Tensor):
                ret.append(torch.minimum(block1, block2))
            else:
                ret.append(np.minimum(block1, block2))

        return ret

    mapper_func = functools.partial(
        _mapper,
        op_bids=operable_blocks
    )

    reduce_ret = df.block_table.mapValues(mapper_func).reduce(_reducer)
    return _post_process(reduce_ret, operable_blocks, data_manager)


def max(df: "DataFrame"):
    data_manager = df.data_manager
    operable_blocks = data_manager.infer_operable_blocks()

    def _mapper(blocks, op_bids):
        ret = []
        for bid in op_bids:
            if isinstance(blocks[bid], torch.Tensor):
                ret.append(blocks[bid].max(axis=0).values)
            else:
                ret.append(blocks[bid].max(axis=0))

        return ret

    def _reducer(blocks1, blocks2):
        ret = []
        for block1, block2 in zip(blocks1, blocks2):
            if isinstance(block1, torch.Tensor):
                ret.append(torch.maximum(block1, block2))
            else:
                ret.append(np.maximum(block1, block2))

        return ret

    mapper_func = functools.partial(
        _mapper,
        op_bids=operable_blocks
    )

    reduce_ret = df.block_table.mapValues(mapper_func).reduce(_reducer)
    return _post_process(reduce_ret, operable_blocks, data_manager)


def sum(df: DataFrame) -> "pd.Series":
    data_manager = df.data_manager
    operable_blocks = data_manager.infer_operable_blocks()

    def _mapper(blocks, op_bids):
        ret = []
        for bid in op_bids:
            ret.append(blocks[bid].sum(axis=0))

        return ret

    def _reducer(blocks1, blocks2):
        return [block1 + block2 for block1, block2 in zip(blocks1, blocks2)]

    mapper_func = functools.partial(
        _mapper,
        op_bids=operable_blocks
    )

    reduce_ret = df.block_table.mapValues(mapper_func).reduce(_reducer)
    return _post_process(reduce_ret, operable_blocks, data_manager)


def mean(df: "DataFrame") -> "pd.Series":
    return sum(df) / df.shape[0]


def _post_process(reduce_ret, operable_blocks, data_manager: "DataManager") -> "pd.Series":
    field_names = data_manager.infer_operable_field_names()
    field_indexes = [data_manager.get_field_offset(name) for name in field_names]
    field_indexes_loc = dict(zip(field_indexes, range(len(field_indexes))))
    ret = [[] for i in range(len(field_indexes))]

    block_type = None

    reduce_ret = [r.tolist() for r in reduce_ret]
    for idx, bid in enumerate(operable_blocks):
        field_indexes = data_manager.blocks[bid].field_indexes
        for offset, field_index in enumerate(field_indexes):
            loc = field_indexes_loc[field_index]
            ret[loc] = reduce_ret[idx][offset]

        if block_type is None:
            block_type = data_manager.blocks[bid].block_type
        elif block_type < data_manager.blocks[bid].block_type:
            block_type = data_manager.blocks[bid].block_type

    return pd.Series(ret, index=field_names, dtype=block_type.value)