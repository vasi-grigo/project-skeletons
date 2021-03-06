# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pyskull.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pyskull.proto',
  package='pyskull',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\rpyskull.proto\x12\x07pyskull\"\x1b\n\x0bHailRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"-\n\x0cHailResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x0c\n\x04\x63ode\x18\x02 \x01(\x05\x32@\n\x07Greeter\x12\x35\n\x04Hail\x12\x14.pyskull.HailRequest\x1a\x15.pyskull.HailResponse\"\x00\x62\x06proto3')
)




_HAILREQUEST = _descriptor.Descriptor(
  name='HailRequest',
  full_name='pyskull.HailRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='pyskull.HailRequest.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=26,
  serialized_end=53,
)


_HAILRESPONSE = _descriptor.Descriptor(
  name='HailResponse',
  full_name='pyskull.HailResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='pyskull.HailResponse.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='code', full_name='pyskull.HailResponse.code', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=55,
  serialized_end=100,
)

DESCRIPTOR.message_types_by_name['HailRequest'] = _HAILREQUEST
DESCRIPTOR.message_types_by_name['HailResponse'] = _HAILRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

HailRequest = _reflection.GeneratedProtocolMessageType('HailRequest', (_message.Message,), dict(
  DESCRIPTOR = _HAILREQUEST,
  __module__ = 'pyskull_pb2'
  # @@protoc_insertion_point(class_scope:pyskull.HailRequest)
  ))
_sym_db.RegisterMessage(HailRequest)

HailResponse = _reflection.GeneratedProtocolMessageType('HailResponse', (_message.Message,), dict(
  DESCRIPTOR = _HAILRESPONSE,
  __module__ = 'pyskull_pb2'
  # @@protoc_insertion_point(class_scope:pyskull.HailResponse)
  ))
_sym_db.RegisterMessage(HailResponse)



_GREETER = _descriptor.ServiceDescriptor(
  name='Greeter',
  full_name='pyskull.Greeter',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=102,
  serialized_end=166,
  methods=[
  _descriptor.MethodDescriptor(
    name='Hail',
    full_name='pyskull.Greeter.Hail',
    index=0,
    containing_service=None,
    input_type=_HAILREQUEST,
    output_type=_HAILRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_GREETER)

DESCRIPTOR.services_by_name['Greeter'] = _GREETER

# @@protoc_insertion_point(module_scope)
