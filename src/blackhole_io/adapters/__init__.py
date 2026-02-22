from io import BytesIO
from typing import Union

from starlette.datastructures import UploadFile

UploadFileType = Union[str, bytes, BytesIO, UploadFile]
