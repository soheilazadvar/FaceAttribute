# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: image_processing.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16image_processing.proto\x12\x10image_processing\"\"\n\x0cImageRequest\x12\x12\n\nimage_data\x18\x01 \x01(\x0c\"F\n\x10LandmarkResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07runtime\x18\x02 \x01(\x01\x12\x11\n\tredis_key\x18\x03 \x01(\t\"G\n\x11\x41geGenderResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0f\n\x07runtime\x18\x02 \x01(\x01\x12\x11\n\tredis_key\x18\x03 \x01(\t\"H\n\x0eStorageRequest\x12\x12\n\nimage_data\x18\x01 \x01(\x0c\x12\x11\n\tredis_key\x18\x02 \x01(\t\x12\x0f\n\x07runtime\x18\x03 \x01(\x01\"!\n\x0fStorageResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\"\xa3\x01\n\x10\x43ombinedResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12=\n\x11landmark_response\x18\x02 \x01(\x0b\x32\".image_processing.LandmarkResponse\x12@\n\x13\x61ge_gender_response\x18\x03 \x01(\x0b\x32#.image_processing.AgeGenderResponse2b\n\nImageInput\x12T\n\x0cProcessImage\x12\x1e.image_processing.ImageRequest\x1a\".image_processing.CombinedResponse\"\x00\x32p\n\x15\x46\x61\x63\x65LandmarkDetection\x12W\n\x0f\x44\x65tectLandmarks\x12\x1e.image_processing.ImageRequest\x1a\".image_processing.LandmarkResponse\"\x00\x32q\n\x13\x41geGenderEstimation\x12Z\n\x11\x45stimateAgeGender\x12\x1e.image_processing.ImageRequest\x1a#.image_processing.AgeGenderResponse\"\x00\x32\x61\n\x0b\x44\x61taStorage\x12R\n\tStoreData\x12 .image_processing.StorageRequest\x1a!.image_processing.StorageResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'image_processing_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_IMAGEREQUEST']._serialized_start=44
  _globals['_IMAGEREQUEST']._serialized_end=78
  _globals['_LANDMARKRESPONSE']._serialized_start=80
  _globals['_LANDMARKRESPONSE']._serialized_end=150
  _globals['_AGEGENDERRESPONSE']._serialized_start=152
  _globals['_AGEGENDERRESPONSE']._serialized_end=223
  _globals['_STORAGEREQUEST']._serialized_start=225
  _globals['_STORAGEREQUEST']._serialized_end=297
  _globals['_STORAGERESPONSE']._serialized_start=299
  _globals['_STORAGERESPONSE']._serialized_end=332
  _globals['_COMBINEDRESPONSE']._serialized_start=335
  _globals['_COMBINEDRESPONSE']._serialized_end=498
  _globals['_IMAGEINPUT']._serialized_start=500
  _globals['_IMAGEINPUT']._serialized_end=598
  _globals['_FACELANDMARKDETECTION']._serialized_start=600
  _globals['_FACELANDMARKDETECTION']._serialized_end=712
  _globals['_AGEGENDERESTIMATION']._serialized_start=714
  _globals['_AGEGENDERESTIMATION']._serialized_end=827
  _globals['_DATASTORAGE']._serialized_start=829
  _globals['_DATASTORAGE']._serialized_end=926
# @@protoc_insertion_point(module_scope)
