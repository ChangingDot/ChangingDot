# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: feedback_server.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x66\x65\x65\x64\x62\x61\x63k_server.proto\x12\x0f\x66\x65\x65\x64\x62\x61\x63k_server\"*\n\x16HasSyntaxErrorsRequest\x12\x10\n\x08\x66ilePath\x18\x01 \x01(\t\"/\n\x14HasSyntaxErrorsReply\x12\x17\n\x0fHasSyntaxErrors\x18\x01 \x01(\x08\"+\n\x17GetCompileErrorsRequest\x12\x10\n\x08\x66ilePath\x18\x01 \x01(\t\"?\n\x15GetCompileErrorsReply\x12&\n\x06\x45rrors\x18\x01 \x03(\x0b\x32\x16.feedback_server.Error\"S\n\x05\x45rror\x12\x11\n\terrorText\x18\x01 \x01(\t\x12\x13\n\x0bprojectName\x18\x02 \x01(\t\x12\x10\n\x08\x66ilePath\x18\x03 \x01(\t\x12\x10\n\x08position\x18\x04 \x03(\x05\x32\xd9\x01\n\x0e\x46\x65\x65\x64\x62\x61\x63kServer\x12\x64\n\x10GetCompileErrors\x12(.feedback_server.GetCompileErrorsRequest\x1a&.feedback_server.GetCompileErrorsReply\x12\x61\n\x0fHasSyntaxErrors\x12\'.feedback_server.HasSyntaxErrorsRequest\x1a%.feedback_server.HasSyntaxErrorsReplyB\x11\xaa\x02\x0e\x44otnetAnalyzerb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'feedback_server_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\252\002\016DotnetAnalyzer'
  _globals['_HASSYNTAXERRORSREQUEST']._serialized_start=42
  _globals['_HASSYNTAXERRORSREQUEST']._serialized_end=84
  _globals['_HASSYNTAXERRORSREPLY']._serialized_start=86
  _globals['_HASSYNTAXERRORSREPLY']._serialized_end=133
  _globals['_GETCOMPILEERRORSREQUEST']._serialized_start=135
  _globals['_GETCOMPILEERRORSREQUEST']._serialized_end=178
  _globals['_GETCOMPILEERRORSREPLY']._serialized_start=180
  _globals['_GETCOMPILEERRORSREPLY']._serialized_end=243
  _globals['_ERROR']._serialized_start=245
  _globals['_ERROR']._serialized_end=328
  _globals['_FEEDBACKSERVER']._serialized_start=331
  _globals['_FEEDBACKSERVER']._serialized_end=548
# @@protoc_insertion_point(module_scope)
