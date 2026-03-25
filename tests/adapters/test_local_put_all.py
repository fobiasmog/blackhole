from io import BytesIO
from pathlib import Path

import pytest
from starlette.datastructures import UploadFile

from blackhole_io.blackhole_file import BlackholeFile


@pytest.mark.asyncio
async def test_put_all_bytes(adapter, tmp_path):
    raw_files = [b"file1", b"file2", b"file3"]
    files = [BlackholeFile(filename=f"f{i}", data_to_upload=d) for i, d in enumerate(raw_files)]
    results = await adapter.put_all(files)
    assert len(results) == 3
    for i, result in enumerate(results):
        with open(tmp_path / result.filename, "rb") as f:
            assert f.read() == raw_files[i]
        assert result.hashsum


@pytest.mark.asyncio
async def test_put_all_mixed_types(adapter, tmp_path):
    source = tmp_path / "mix.txt"
    source.write_bytes(b"from path")
    upload = UploadFile(file=BytesIO(b"from upload"), filename="up.bin")

    files = [
        BlackholeFile(filename="raw", data_to_upload=b"raw"),
        BlackholeFile(filename="path", data_to_upload=str(source)),
        BlackholeFile(filename="up.bin", data_to_upload=upload),
    ]
    results = await adapter.put_all(files)
    assert len(results) == 3

    assert Path(results[0].filename).suffix == ""
    assert Path(results[1].filename).suffix == ".txt"
    assert Path(results[2].filename).suffix == ".bin"


@pytest.mark.asyncio
async def test_put_all_empty(adapter):
    results = await adapter.put_all([])
    assert results == []
