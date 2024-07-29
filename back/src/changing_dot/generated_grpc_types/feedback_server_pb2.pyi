from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HasSyntaxErrorsRequest(_message.Message):
    __slots__ = ("filePath",)
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    filePath: str
    def __init__(self, filePath: _Optional[str] = ...) -> None: ...

class HasSyntaxErrorsReply(_message.Message):
    __slots__ = ("HasSyntaxErrors",)
    HASSYNTAXERRORS_FIELD_NUMBER: _ClassVar[int]
    HasSyntaxErrors: bool
    def __init__(self, HasSyntaxErrors: bool = ...) -> None: ...

class GetCompileErrorsRequest(_message.Message):
    __slots__ = ("filePath",)
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    filePath: str
    def __init__(self, filePath: _Optional[str] = ...) -> None: ...

class GetCompileErrorsReply(_message.Message):
    __slots__ = ("Errors",)
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    Errors: _containers.RepeatedCompositeFieldContainer[Error]
    def __init__(self, Errors: _Optional[_Iterable[_Union[Error, _Mapping]]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("errorText", "projectName", "filePath", "position")
    ERRORTEXT_FIELD_NUMBER: _ClassVar[int]
    PROJECTNAME_FIELD_NUMBER: _ClassVar[int]
    FILEPATH_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    errorText: str
    projectName: str
    filePath: str
    position: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, errorText: _Optional[str] = ..., projectName: _Optional[str] = ..., filePath: _Optional[str] = ..., position: _Optional[_Iterable[int]] = ...) -> None: ...
