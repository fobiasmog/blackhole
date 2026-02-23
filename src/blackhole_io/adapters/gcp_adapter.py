from blackhole_io.adapters import UploadFileType
from blackhole_io.adapters.abstract import AbstractAdapter
from blackhole_io.blackhole_file import BlackholeFile


class GCPAdapter(AbstractAdapter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def put(self, file: UploadFileType) -> str:
        print("[GCPAdapter] PUT")
        return ""

    async def put_all(self, files: list[UploadFileType]) -> list[str]:
        print("[GCPAdapter] PUT ALL")
        return [""] * len(files)

    async def get(self, file_name: str) -> BlackholeFile:
        print("[GCPAdapter] GET")
        return BlackholeFile(filename=file_name)

    async def exists(self, file_name: str) -> bool:
        print("[GCPAdapter] EXISTS")
        return False

    async def delete(self, file_name: str) -> None:
        print("[GCPAdapter] DELETE")
        pass
