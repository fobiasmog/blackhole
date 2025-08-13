from typing import Union
from io import BytesIO
from starlette.datastructures import UploadFile

UploadFileType = Union[str, bytes, BytesIO, UploadFile]
