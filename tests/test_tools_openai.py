"""Tests for blackhole_io.tools.openai"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Lightweight FunctionTool stand-in so we don't need `openai-agents` installed
# ---------------------------------------------------------------------------
@dataclass
class _FakeFunctionTool:
    name: str = ""
    description: str = ""
    params_json_schema: dict[str, Any] = field(default_factory=dict)
    on_invoke_tool: Callable[..., Any] | None = None


_fake_agents = MagicMock()
_fake_agents.FunctionTool = _FakeFunctionTool
sys.modules.setdefault("agents", _fake_agents)

from blackhole_io.tools.openai import BlackholeOpenAITools  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Definition tests
# ---------------------------------------------------------------------------
def test_definitions_returns_all_operations():
    tools = BlackholeOpenAITools(_make_bh())
    defs = tools.definitions()
    names = {d.name for d in defs}
    assert names == {
        "blackhole_put",
        "blackhole_get",
        "blackhole_exists",
        "blackhole_delete",
    }


def test_definitions_have_valid_schemas():
    tools = BlackholeOpenAITools(_make_bh())
    for defn in tools.definitions():
        assert defn.params_json_schema["type"] == "object"
        assert "properties" in defn.params_json_schema


def test_definitions_descriptions_non_empty():
    tools = BlackholeOpenAITools(_make_bh())
    for defn in tools.definitions():
        assert len(defn.description) > 20


def test_definitions_have_on_invoke_tool():
    tools = BlackholeOpenAITools(_make_bh())
    for defn in tools.definitions():
        assert callable(defn.on_invoke_tool)


# ---------------------------------------------------------------------------
# handle() tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_handle_put_success(tmp_path):
    bh = _make_bh(put_return="uploads/file.txt")
    tools = BlackholeOpenAITools(bh)
    content = b"hello world"
    f = tmp_path / "file.txt"
    f.write_bytes(content)
    result = await tools.handle(
        "blackhole_put",
        {"file_path": str(f), "filename": "file.txt"},
    )
    payload = json.loads(result)
    assert payload["filename"] == "uploads/file.txt"
    assert payload["size"] == len(content)
    bh.put.assert_called_once()


@pytest.mark.asyncio
async def test_handle_put_passes_filename(tmp_path):
    bh = _make_bh()
    tools = BlackholeOpenAITools(bh)
    f = tmp_path / "my_file.txt"
    f.write_bytes(b"data")
    await tools.handle(
        "blackhole_put",
        {"file_path": str(f), "filename": "my_file.txt"},
    )
    call_args = bh.put.call_args
    assert call_args[1]["filename"] == "my_file.txt"


@pytest.mark.asyncio
async def test_handle_put_missing_file():
    tools = BlackholeOpenAITools(_make_bh())
    result = await tools.handle(
        "blackhole_put", {"file_path": "/nonexistent/file.txt"}
    )
    payload = json.loads(result)
    assert "error" in payload


@pytest.mark.asyncio
async def test_handle_put_uses_path_name_as_default_filename(tmp_path):
    bh = _make_bh()
    tools = BlackholeOpenAITools(bh)
    f = tmp_path / "report.pdf"
    f.write_bytes(b"pdf content")
    await tools.handle("blackhole_put", {"file_path": str(f)})
    call_args = bh.put.call_args
    assert call_args[1]["filename"] == "report.pdf"


@pytest.mark.asyncio
async def test_handle_get_success():
    blob = b"file content here"
    bh = _make_bh(get_blob=blob)
    tools = BlackholeOpenAITools(bh)
    result = await tools.handle("blackhole_get", {"filename": "stored.txt"})
    payload = json.loads(result)
    assert payload["filename"] == "stored.txt"
    assert "file_path" in payload
    tmp = Path(payload["file_path"])
    assert tmp.exists()
    assert tmp.read_bytes() == blob
    tmp.unlink()


@pytest.mark.asyncio
async def test_handle_exists_true():
    tools = BlackholeOpenAITools(_make_bh(exists_return=True))
    result = await tools.handle("blackhole_exists", {"filename": "foo.txt"})
    assert json.loads(result)["exists"] is True


@pytest.mark.asyncio
async def test_handle_exists_false():
    tools = BlackholeOpenAITools(_make_bh(exists_return=False))
    result = await tools.handle("blackhole_exists", {"filename": "missing.txt"})
    assert json.loads(result)["exists"] is False


@pytest.mark.asyncio
async def test_handle_delete_success():
    bh = _make_bh()
    tools = BlackholeOpenAITools(bh)
    result = await tools.handle("blackhole_delete", {"filename": "old.txt"})
    payload = json.loads(result)
    assert payload["deleted"] is True
    bh.delete.assert_called_once_with("old.txt")


@pytest.mark.asyncio
async def test_handle_unknown_tool_raises():
    tools = BlackholeOpenAITools(_make_bh())
    with pytest.raises(ValueError, match="Unknown Blackhole tool"):
        await tools.handle("blackhole_fly_to_moon", {})


@pytest.mark.asyncio
async def test_handle_wraps_adapter_exception():
    bh = _make_bh()
    bh.get = AsyncMock(side_effect=FileNotFoundError("not found"))
    tools = BlackholeOpenAITools(bh)
    result = await tools.handle("blackhole_get", {"filename": "ghost.txt"})
    assert "error" in json.loads(result)


# ---------------------------------------------------------------------------
# on_invoke_tool callback test
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_on_invoke_tool_callback(tmp_path):
    bh = _make_bh(exists_return=True)
    tools = BlackholeOpenAITools(bh)
    defs = tools.definitions()
    exists_tool = next(d for d in defs if d.name == "blackhole_exists")

    result = await exists_tool.on_invoke_tool(
        None,  # ctx — unused by Blackhole tools
        json.dumps({"filename": "check.txt"}),
    )
    payload = json.loads(result)
    assert payload["exists"] is True
    assert payload["filename"] == "check.txt"
