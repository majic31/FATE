# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: hetero-kmeans-meta.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18hetero-kmeans-meta.proto\x12&com.webank.ai.fate.core.mlmodel.buffer\";\n\x0fKmeansModelMeta\x12\t\n\x01k\x18\x01 \x01(\x03\x12\x0b\n\x03tol\x18\x02 \x01(\x01\x12\x10\n\x08max_iter\x18\x03 \x01(\x03\x42\x16\x42\x14KmeansModelMetaProtob\x06proto3')



_KMEANSMODELMETA = DESCRIPTOR.message_types_by_name['KmeansModelMeta']
KmeansModelMeta = _reflection.GeneratedProtocolMessageType('KmeansModelMeta', (_message.Message,), {
  'DESCRIPTOR' : _KMEANSMODELMETA,
  '__module__' : 'hetero_kmeans_meta_pb2'
  # @@protoc_insertion_point(class_scope:com.webank.ai.fate.core.mlmodel.buffer.KmeansModelMeta)
  })
_sym_db.RegisterMessage(KmeansModelMeta)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'B\024KmeansModelMetaProto'
  _KMEANSMODELMETA._serialized_start=68
  _KMEANSMODELMETA._serialized_end=127
# @@protoc_insertion_point(module_scope)