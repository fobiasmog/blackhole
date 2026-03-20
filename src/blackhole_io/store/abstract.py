from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blackhole_io.store.models import FileRecord, FileRecordInput


class AbstractStore(ABC):
    @abstractmethod
    async def save(self, record: "FileRecordInput") -> "FileRecord":
        pass

    @abstractmethod
    async def get(self, filename: str) -> "FileRecord | None":
        pass

    @abstractmethod
    async def delete(self, filename: str) -> None:
        pass

    @abstractmethod
    async def create_tables(self) -> None:
        pass
