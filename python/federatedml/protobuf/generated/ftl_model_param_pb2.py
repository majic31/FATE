# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ftl-model-param.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x66tl-model-param.proto\x12&com.webank.ai.fate.core.mlmodel.buffer\"C\n\rFTLModelParam\x12\x13\n\x0bmodel_bytes\x18\x01 \x01(\x0c\x12\r\n\x05phi_a\x18\x02 \x03(\x01\x12\x0e\n\x06header\x18\x03 \x03(\tB\x14\x42\x12\x46TLModelParamProtob\x06proto3')



_FTLMODELPARAM = DESCRIPTOR.message_types_by_name['FTLModelParam']
FTLModelParam = _reflection.GeneratedProtocolMessageType('FTLModelParam', (_message.Message,), {
  'DESCRIPTOR' : _FTLMODELPARAM,
  '__module__' : 'ftl_model_param_pb2'
  # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.FTLModelParam)
  })
_sym_db.RegisterMessage(FTLModelParam)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'B\022FTLModelParamProto'
  _FTLMODELPARAM._serialized_start=65
  _FTLMODELPARAM._serialized_end=132
# @@protoc_insertion_point(module_scope)