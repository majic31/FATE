# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sir-param.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fsir-param.proto\x12(com.webank.ai.fate.common.mlmodel.buffer\"F\n\x1fSecureInformationRetrievalParam\x12\x10\n\x08\x63overage\x18\x01 \x01(\x01\x12\x11\n\tblock_num\x18\x02 \x01(\x03\x42\x0f\x42\rSIRParamProtob\x06proto3')



_SECUREINFORMATIONRETRIEVALPARAM = DESCRIPTOR.message_types_by_name['SecureInformationRetrievalParam']
SecureInformationRetrievalParam = _reflection.GeneratedProtocolMessageType('SecureInformationRetrievalParam', (_message.Message,), {
  'DESCRIPTOR' : _SECUREINFORMATIONRETRIEVALPARAM,
  '__module__' : 'sir_param_pb2'
  # @@protoc_insertion_point(class_scope:com.webank.ai.fate.common.mlmodel.buffer.SecureInformationRetrievalParam)
  })
_sym_db.RegisterMessage(SecureInformationRetrievalParam)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'B\rSIRParamProto'
  _SECUREINFORMATIONRETRIEVALPARAM._serialized_start=61
  _SECUREINFORMATIONRETRIEVALPARAM._serialized_end=131
# @@protoc_insertion_point(module_scope)
