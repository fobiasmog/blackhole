### BlackholeFile
# Object of this class represents the information about uploaded/downloaded file

from pydantic import BaseModel, ConfigDict, Field

from blackhole_io.types import UploadFileType


class BlackholeFile(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    filename: str = Field(..., description="The name/key of the file in storage")
    content_type: str = Field(default="application/octet-stream")
    size: int = Field(default=0)
    data: bytes = Field(default=b"", repr=False)
    data_to_upload: UploadFileType = Field(default=b"", repr=False)
    extra: dict = Field(default_factory=dict)

    @property
    def blob(self) -> bytes:
        return self.data
