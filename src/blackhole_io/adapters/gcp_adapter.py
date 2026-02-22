from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.abstract import AbstractAdapter


class GCPAdapter(AbstractAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def put(self, file: UploadFileType) -> str:
        print("[GCPAdapter] PUT")
        return ""

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        print("[GCPAdapter] PUT ALL")
        return [""] * len(files)

    async def get(self, file_name: str) -> UploadFileType:
        print("[GCPAdapter] GET")
        return ""

    async def delete(self, file_name: str) -> None:
        print("[GCPAdapter] DELETE")
        pass
