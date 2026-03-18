from io import BytesIO
from pathlib import Path

import pytest
from starlette.datastructures import UploadFile


@pytest.mark.asyncio
async def test_put_all_bytes(adapter):
    files = [b"file1", b"file2", b"file3"]
    filenames = await adapter.put_all(files)
    assert len(filenames) == 3
    for i, fname in enumerate(filenames):
        with open(fname, "rb") as f:
            assert f.read() == files[i]


@pytest.mark.asyncio
async def test_put_all_mixed_types(adapter, tmp_path):
    source = tmp_path / "mix.txt"
    source.write_bytes(b"from path")
    upload = UploadFile(file=BytesIO(b"from upload"), filename="up.bin")

    files = [b"raw", str(source), upload]
    filenames = await adapter.put_all(files)
    assert len(filenames) == 3

    assert Path(filenames[0]).suffix == ""
    assert Path(filenames[1]).suffix == ".txt"
    assert Path(filenames[2]).suffix == ".bin"


@pytest.mark.asyncio
async def test_put_all_empty(adapter):
    filenames = await adapter.put_all([])
    assert filenames == []
