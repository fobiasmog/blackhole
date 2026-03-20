from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, SQLModel


class FileRecord(SQLModel, table=True):
    __tablename__ = "blackhole_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(index=True, unique=True)
    content_type: Optional[str] = Field(default=None)
    size: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extra_metadata: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column("metadata", JSON)
    )


class FileRecordInput(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"
    size: int = 0
    extra_metadata: Optional[dict[str, Any]] = None
