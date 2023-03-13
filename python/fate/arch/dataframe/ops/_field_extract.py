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
import pandas as pd
from .._dataframe import DataFrame


def field_extract(fate_df: "DataFrame", with_sample_id=True, with_match_id=True, with_weight=True,
                  with_label=True, columns=None):
    """
    blocks_loc: list, each element: (src_block_id, dst_block_id, changed=True/False, block_indexes)
    """
    def _extract_columns(src_blocks):
        extract_blocks = [None] * len(blocks_loc)

        for src_block_id, dst_block_id, is_changed, block_column_indexes in blocks_loc:
            block = src_blocks[src_block_id]
            if is_changed:
                """
                multiple columns, maybe pandas or fate.arch.tensor object
                """
                if isinstance(block, pd.DataFrame):
                    extract_blocks[dst_block_id] = block.iloc[:, block_column_indexes]
                else:
                    extract_blocks[dst_block_id] = block[:, block_column_indexes]
            else:
                extract_blocks[dst_block_id] = block

        return extract_blocks

    data_manager, blocks_loc = fate_df.data_manager.derive_new_data_manager(
        with_sample_id=with_sample_id,
        with_match_id=with_match_id,
        with_label=with_label,
        with_weight=with_weight,
        columns=columns
    )
    extract_table = fate_df.block_table.mapValues(_extract_columns)

    return DataFrame(
        fate_df._ctx,
        extract_table,
        partition_order_mappings=fate_df.partition_order_mappings,
        data_manager=data_manager
    )