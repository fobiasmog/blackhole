### BlackholeFile
# Object of this class represents the information about uploaded/downloaded file

from pydantic import BaseModel, Field


class BlackholeFile(BaseModel):
    filename: str = Field(..., description="The name/key of the file in storage")
    content_type: str = Field(default="application/octet-stream")
    size: int = Field(default=0)
    data: bytes = Field(default=b"", repr=False)
    data_to_upload: bytes = Field(default=b"", repr=False)

    @property
    def blob(self) -> bytes:
        return self.data
