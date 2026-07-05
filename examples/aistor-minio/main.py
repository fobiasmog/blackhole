import logging
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from blackhole_io import Blackhole

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "blackhole.yaml"


class HealthResponse(BaseModel):
    status: str


class UploadResponse(BaseModel):
    filename: str


@lru_cache
def get_blackhole() -> Blackhole:
    if CONFIG_PATH.exists():
        return Blackhole(config=CONFIG_PATH)
    return Blackhole()


def get_blackhole_dependency() -> Blackhole:
    return get_blackhole()


app = FastAPI(title="AIStor MinIO Example API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@app.put("/files", response_model=list[UploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_file(
    files: Annotated[list[UploadFile], File(...)],
    blackhole: Annotated[Blackhole, Depends(get_blackhole_dependency)],
    filename: str | None = None,
) -> list[UploadResponse]:
    stored_filenames = []
    try:
        for file in files:
            stored_filename = await blackhole.put(file=file, filename=filename)
            stored_filenames.append(stored_filename)
    except Exception as exc:
        logger.exception("Failed to upload file")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file",
        ) from exc

    return [UploadResponse(filename=fn) for fn in stored_filenames]
