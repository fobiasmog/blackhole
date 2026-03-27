"""Tests for blackhole_io.tools.anthropic"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from blackhole_io.tools.anthropic import (BlackholeAnthropicTools,
                                          _build_json_schema)
from blackhole_io.tools.base import ToolParam


def _make_bh(*, put_return="stored.txt", get_blob=b"hello", exists_return=True):
    bh = MagicMock()
    bh_file = MagicMock()
    bh_file.filename = "stored.txt"
    bh_file.content_type = "text/plain"
    bh_file.size = len(get_blob)
    bh_file.blob = get_blob
    bh.put = AsyncMock(return_value=put_return)
    bh.get = AsyncMock(return_value=bh_file)
    bh.exists = AsyncMock(return_value=exists_return)
    bh.delete = AsyncMock(return_value=None)
    return bh


def test_build_json_schema_required_only():
    params = [
        ToolParam("foo", "string", "A foo param", required=True),
        ToolParam("bar", "integer", "A bar param", required=True),
    ]
    schema = _build_json_schema(params)
    assert schema["type"] == "object"
    assert "foo" in schema["properties"]
    assert schema["required"] == ["foo", "bar"]


def test_build_json_schema_optional_not_in_required():
    params = [
        ToolParam("req", "string", "required", required=True),
        ToolParam("opt", "string", "optional", required=False),
    ]
    schema = _build_json_schema(params)
    assert "req" in schema["required"]
    assert "opt" not in schema.get("required", [])


def test_build_json_schema_enum():
    params = [ToolParam("mode", "string", "mode", enum=["a", "b"])]
    schema = _build_json_schema(params)
    assert schema["properties"]["mode"]["enum"] == ["a", "b"]


def test_definitions_returns_all_operations():
    tools = BlackholeAnthropicTools(_make_bh())
    names = {d["name"] for d in tools.definitions()}
    assert names == {
        "blackhole_put",
        "blackhole_get",
        "blackhole_exists",
        "blackhole_delete",
    }


def test_definitions_have_required_keys():
    tools = BlackholeAnthropicTools(_make_bh())
    for defn in tools.definitions():
        assert "name" in defn
        assert "description" in defn
        assert "input_schema" in defn
        assert defn["input_schema"]["type"] == "object"


def test_definitions_descriptions_non_empty():
    tools = BlackholeAnthropicTools(_make_bh())
    for defn in tools.definitions():
        assert len(defn["description"]) > 20


@pytest.mark.asyncio
async def test_handle_put_success(tmp_path):
    bh = _make_bh(put_return="uploads/file.txt")
    tools = BlackholeAnthropicTools(bh)
    content = b"hello world"
    f = tmp_path / "file.txt"
    f.write_bytes(content)
    result = await tools.handle(
        "blackhole_put",
        {"file_path": str(f), "filename": "file.txt"},
        tool_use_id="tu_001",
    )
    assert result["type"] == "tool_result"
    assert result["tool_use_id"] == "tu_001"
    payload = json.loads(result["content"])
    assert payload["filename"] == "uploads/file.txt"
    assert payload["size"] == len(content)
    bh.put.assert_called_once()


@pytest.mark.asyncio
async def test_handle_put_passes_filename(tmp_path):
    bh = _make_bh()
    tools = BlackholeAnthropicTools(bh)
    f = tmp_path / "my_file.txt"
    f.write_bytes(b"data")
    await tools.handle(
        "blackhole_put",
        {"file_path": str(f), "filename": "my_file.txt"},
    )
    call_args = bh.put.call_args
    assert call_args[1]["filename"] == "my_file.txt"


@pytest.mark.asyncio
async def test_handle_put_reads_file_from_path(tmp_path):
    bh = _make_bh()
    tools = BlackholeAnthropicTools(bh)
    content = b"\x00\x01\x02\x03binary"
    f = tmp_path / "binary.bin"
    f.write_bytes(content)
    await tools.handle("blackhole_put", {"file_path": str(f)})
    call_arg = bh.put.call_args[0][0]
    assert isinstance(call_arg, str)
    assert call_arg == str(f)


@pytest.mark.asyncio
async def test_handle_put_missing_file():
    bh = _make_bh()
    tools = BlackholeAnthropicTools(bh)
    result = await tools.handle(
        "blackhole_put", {"file_path": "/nonexistent/file.txt"}
    )
    payload = json.loads(result["content"])
    assert "error" in payload


@pytest.mark.asyncio
async def test_handle_put_uses_path_name_as_default_filename(tmp_path):
    bh = _make_bh()
    tools = BlackholeAnthropicTools(bh)
    f = tmp_path / "report.pdf"
    f.write_bytes(b"pdf content")
    await tools.handle("blackhole_put", {"file_path": str(f)})
    call_args = bh.put.call_args
    assert call_args[1]["filename"] == "report.pdf"


@pytest.mark.asyncio
async def test_handle_get_success():
    blob = b"file content here"
    bh = _make_bh(get_blob=blob)
    tools = BlackholeAnthropicTools(bh)
    result = await tools.handle("blackhole_get", {"filename": "stored.txt"}, "tu_002")
    payload = json.loads(result["content"])
    assert payload["filename"] == "stored.txt"
    assert "file_path" in payload
    tmp = Path(payload["file_path"])
    assert tmp.exists()
    assert tmp.read_bytes() == blob
    tmp.unlink()


@pytest.mark.asyncio
async def test_handle_exists_true():
    tools = BlackholeAnthropicTools(_make_bh(exists_return=True))
    result = await tools.handle("blackhole_exists", {"filename": "foo.txt"})
    assert json.loads(result["content"])["exists"] is True


@pytest.mark.asyncio
async def test_handle_exists_false():
    tools = BlackholeAnthropicTools(_make_bh(exists_return=False))
    result = await tools.handle("blackhole_exists", {"filename": "missing.txt"})
    assert json.loads(result["content"])["exists"] is False


@pytest.mark.asyncio
async def test_handle_delete_success():
    bh = _make_bh()
    tools = BlackholeAnthropicTools(bh)
    result = await tools.handle("blackhole_delete", {"filename": "old.txt"}, "tu_003")
    payload = json.loads(result["content"])
    assert payload["deleted"] is True
    bh.delete.assert_called_once_with("old.txt")


@pytest.mark.asyncio
async def test_handle_unknown_tool_raises():
    tools = BlackholeAnthropicTools(_make_bh())
    with pytest.raises(ValueError, match="Unknown Blackhole tool"):
        await tools.handle("blackhole_fly_to_moon", {})


@pytest.mark.asyncio
async def test_handle_wraps_adapter_exception():
    bh = _make_bh()
    bh.get = AsyncMock(side_effect=FileNotFoundError("not found"))
    tools = BlackholeAnthropicTools(bh)
    result = await tools.handle("blackhole_get", {"filename": "ghost.txt"})
    assert "error" in json.loads(result["content"])


@pytest.mark.asyncio
async def test_handle_response_processes_tool_use_blocks():
    bh = _make_bh()
    tools = BlackholeAnthropicTools(bh)

    text_block = MagicMock()
    text_block.type = "text"

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.id = "tu_010"
    tool_block.name = "blackhole_exists"
    tool_block.input = {"filename": "check.txt"}

    results = await tools.handle_response([text_block, tool_block])
    assert len(results) == 1
    assert results[0]["tool_use_id"] == "tu_010"


@pytest.mark.asyncio
async def test_handle_response_empty_when_no_tool_use():
    tools = BlackholeAnthropicTools(_make_bh())
    text_block = MagicMock()
    text_block.type = "text"
    assert await tools.handle_response([text_block]) == []
