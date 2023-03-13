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
#
from .schema_manager import SchemaManager
from .block_manager import BlockManager
from .block_manager import BlockType
from ..entity import types
from typing import Union, List, Tuple


class DataManager(object):
    def __init__(self, schema_manager: SchemaManager = None, block_manager: BlockManager = None):
        self._schema_manager = schema_manager
        self._block_manager = block_manager

    @property
    def blocks(self):
        return self._block_manager.blocks

    @property
    def block_num(self):
        return len(self._block_manager.blocks)

    @property
    def schema(self):
        return self._schema_manager.schema

    def append_columns(self, columns: List[str], block_types: Union["BlockType", List["BlockType"]]) -> List[int]:
        field_indexes = self._schema_manager.append_columns(columns, block_types)
        block_indexes = self._block_manager.append_fields(field_indexes, block_types)

        return block_indexes

    def split_columns(self, columns: List[str], block_types: Union["BlockType", List["BlockType"]]):
        field_indexes = self._schema_manager.split_columns(columns, block_types)
        narrow_blocks, dst_blocks = self._block_manager.split_fields(field_indexes, block_types)

        return narrow_blocks, dst_blocks

    def duplicate(self) -> "DataManager":
        return DataManager(
            self._schema_manager.duplicate(),
            self._block_manager.duplicate()
        )

    def init_from_table_schema(self, schema, delimiter, match_id_name, label_name, weight_name,
                               label_type, weight_type, dtype, default_type=types.DEFAULT_DATA_TYPE):
        schema_manager = SchemaManager()
        retrieval_index_dict = schema_manager.parse_table_schema(
            schema=schema,
            delimiter=delimiter,
            match_id_name=match_id_name,
            label_name=label_name,
            weight_name=weight_name
        )

        schema_manager.init_field_types(label_type, weight_type, dtype,
                                        default_type=default_type)
        block_manager = BlockManager()
        block_manager.initialize_blocks(schema_manager)

        self._schema_manager = schema_manager
        self._block_manager = block_manager

        return retrieval_index_dict

    def init_from_local_file(self, sample_id_name, columns, match_id_list, match_id_name, label_name, weight_name,
                             label_type, weight_type, dtype, default_type=types.DEFAULT_DATA_TYPE):
        schema_manager = SchemaManager()
        retrieval_index_dict = schema_manager.parse_local_file_schema(sample_id_name,
                                                                      columns,
                                                                      match_id_list,
                                                                      match_id_name,
                                                                      label_name,
                                                                      weight_name)
        schema_manager.init_field_types(label_type, weight_type, dtype,
                                         default_type=default_type)
        block_manager = BlockManager()
        block_manager.initialize_blocks(schema_manager)

        self._schema_manager = schema_manager
        self._block_manager = block_manager

        return retrieval_index_dict

    def convert_to_blocks(self, splits):
        converted_blocks = []
        for bid, block in enumerate(self._block_manager.blocks):
            converted_blocks.append(block.convert_block(splits[bid]))

        return converted_blocks

    def derive_new_data_manager(self, with_sample_id, with_match_id, with_label, with_weight, columns):
        schema_manager, derive_indexes = self._schema_manager.derive_new_schema_manager(with_sample_id=with_sample_id,
                                                                                        with_match_id=with_match_id,
                                                                                        with_label=with_label,
                                                                                        with_weight=with_weight,
                                                                                        columns=columns)
        block_manager, blocks_loc = self._block_manager.derive_new_block_manager(derive_indexes)

        return DataManager(
            schema_manager=schema_manager,
            block_manager=block_manager
        ), blocks_loc

    def loc_block(self, name: Union[str, List[str]], with_offset=True):
        if isinstance(name, str):
            field_index = self._schema_manager.get_field_offset(name)
            return self._block_manager.loc_block(field_index, with_offset)
        else:
            loc_ret = []
            for _name in name:
                field_index = self._schema_manager.get_field_offset(_name)
                loc_ret.append(self._block_manager.loc_block(field_index, with_offset))

            return loc_ret

    def get_fields_loc(self):
        field_block_mapping = self._block_manager.field_block_mapping
        fields_loc = [[]] * len(field_block_mapping)
        for col_id, _block_id_tuple in field_block_mapping.items():
            fields_loc[col_id] = _block_id_tuple

        return fields_loc

    def get_field_name(self, field_index):
        return self._schema_manager.get_field_name(field_index)

    def get_field_type_by_name(self, name):
        return self._schema_manager.get_field_types(name)

    def get_block(self, block_id):
        return self._block_manager.blocks[block_id]

    def infer_operable_blocks(self):
        operable_field_offsets = self._schema_manager.infer_operable_filed_offsets()
        block_index_set = set(self._block_manager.loc_block(offset, with_offset=False) for offset in operable_field_offsets)
        return sorted(list(block_index_set))

    def infer_operable_field_names(self):
        return self._schema_manager.infer_operable_field_names()

    def infer_non_operable_blocks(self):
        non_operable_field_offsets = self._schema_manager.infer_non_operable_field_offsets()
        block_index_set = set(self._block_manager.loc_block(offset) for offset in non_operable_field_offsets)
        return sorted(list(block_index_set))

    def try_to_promote_types(self,
                             block_indexes: List[int],
                             block_type: Union[list, int, float, BlockType]) -> List[Tuple[int, BlockType]]:
        promote_types = []
        if isinstance(block_type, (int, float)):
            block_type = BlockType.get_block_type(block_type)

        if isinstance(block_type, BlockType):
            for idx, bid in enumerate(block_indexes):
                if self.get_block(bid).block_type < block_type:
                    promote_types.append(
                        (bid, block_type)
                    )
        else:
            for idx, (bid, r_type) in enumerate(zip(block_indexes, list)):
                block_type = BlockType.get_block_type(r_type)
                if self.get_block(bid).block_type < block_type:
                    promote_types.append(
                        (bid, block_type)
                    )

        return promote_types

    def promote_types(self, to_promote_blocks: list):
        for bid, block_type in to_promote_blocks:
            self._block_manager.blocks[bid] = self._block_manager.blocks[bid].convert_block_type(block_type)
            for field_index in self._block_manager.blocks[bid].field_indexes:
                self._schema_manager.set_field_type_by_offset(field_index, block_type.value())

    def compress_blocks(self):
        new_blocks, to_compress_block_loc, non_compress_block_changes = self._block_manager.compress()
        if to_compress_block_loc:
            self._block_manager.reset_blocks(new_blocks)

        return to_compress_block_loc, non_compress_block_changes

    def serialize(self):
        fields = self._schema_manager.serialize()
        for col_id, field in enumerate(fields):
            block_id = self._block_manager.loc_block(col_id, with_offset=False)
            should_compress = self._block_manager.blocks[block_id].should_compress
            field["should_compress"] = should_compress

        return fields

    @classmethod
    def deserialize(cls, fields):
        data_manager = DataManager()
        data_manager._schema_manager = SchemaManager.deserialize(fields)
        data_manager._block_manager = BlockManager()
        data_manager._block_manager.initialize_blocks(data_manager._schema_manager)

        return data_manager