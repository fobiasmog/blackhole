from io import BytesIO
from pathlib import Path

import pytest
from starlette.datastructures import UploadFile

from blackhole_io.blackhole_file import BlackholeFile


@pytest.mark.asyncio
async def test_put_all_bytes(adapter, tmp_path):
    raw_files = [b"file1", b"file2", b"file3"]
    files = [BlackholeFile(filename=f"f{i}", data_to_upload=d) for i, d in enumerate(raw_files)]
    filenames = await adapter.put_all(files)
    assert len(filenames) == 3
    for i, fname in enumerate(filenames):
        with open(tmp_path / fname, "rb") as f:
            assert f.read() == raw_files[i]


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
    filenames = await adapter.put_all(files)
    assert len(filenames) == 3

    assert Path(filenames[0]).suffix == ""
    assert Path(filenames[1]).suffix == ".txt"
    assert Path(filenames[2]).suffix == ".bin"


@pytest.mark.asyncio
async def test_put_all_empty(adapter):
    filenames = await adapter.put_all([])
    assert filenames == []
