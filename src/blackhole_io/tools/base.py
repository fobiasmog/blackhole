"""
Vendor-agnostic tool definitions for Blackhole.

Each OPERATION describes a Blackhole action in a structured way so that
vendor-specific adapters (Anthropic, OpenAI, Google, LangChain, …) can
translate it into their own tool schema format without duplicating the
business logic.
"""

from __future__ import annotations

import mimetypes
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from blackhole_io import Blackhole


@dataclass(frozen=True)
class ToolParam:
    name: str
    type: str  # JSON Schema primitive: "string", "integer", "boolean"
    description: str
    required: bool = True
    enum: list[str] | None = None


@dataclass(frozen=True)
class OperationDef:
    """Vendor-neutral description of one Blackhole tool operation."""

    name: str
    description: str
    params: list[ToolParam] = field(default_factory=list)


OPERATIONS: list[OperationDef] = [
    OperationDef(
        name="blackhole_put",
        description=(
            "Upload a file to Blackhole storage from a local file path. "
            "The tool reads the file directly from disk — never send file "
            "contents through the conversation. "
            "Returns the filename (key) under which the file was stored — "
            "use this key in subsequent get / exists / delete calls."
        ),
        params=[
            ToolParam(
                name="file_path",
                type="string",
                description=(
                    "Absolute path to the file on the local filesystem, "
                    "e.g. '/home/user/documents/report.pdf'."
                ),
            ),
            ToolParam(
                name="filename",
                type="string",
                description=(
                    "Desired filename including extension, e.g. 'report.pdf'. "
                    "If omitted the original filename from the path is used."
                ),
                required=False,
            ),
            ToolParam(
                name="content_type",
                type="string",
                description=(
                    "MIME type of the file, e.g. 'image/png', 'application/pdf', "
                    "'text/plain'. If omitted it will be inferred from the filename."
                ),
                required=False,
            ),
        ],
    ),
    OperationDef(
        name="blackhole_get",
        description=(
            "Retrieve a file from Blackhole storage by its filename (key). "
            "Returns the file metadata (filename, content_type, size in bytes) "
            "and a local file_path where the content has been written. "
            "Use this tool when you need to read or process a previously stored file."
        ),
        params=[
            ToolParam(
                name="filename",
                type="string",
                description="The exact filename (key) returned by blackhole_put.",
            ),
        ],
    ),
    OperationDef(
        name="blackhole_exists",
        description=(
            "Check whether a file exists in Blackhole storage. "
            "Returns a boolean result. "
            "Use this before attempting to get or delete a file when you are "
            "unsure whether it was already uploaded."
        ),
        params=[
            ToolParam(
                name="filename",
                type="string",
                description="The filename (key) to check.",
            ),
        ],
    ),
    OperationDef(
        name="blackhole_delete",
        description=(
            "Permanently delete a file from Blackhole storage. "
            "Returns a confirmation message. "
            "Use this tool to clean up files that are no longer needed."
        ),
        params=[
            ToolParam(
                name="filename",
                type="string",
                description="The filename (key) of the file to delete.",
            ),
        ],
    ),
]

OPERATION_MAP: dict[str, OperationDef] = {op.name: op for op in OPERATIONS}


def build_json_schema(params: list[ToolParam]) -> dict[str, Any]:
    """Convert a list of ToolParam into a JSON Schema object dict."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in params:
        prop: dict[str, Any] = {"type": p.type, "description": p.description}
        if p.enum:
            prop["enum"] = p.enum
        properties[p.name] = prop
        if p.required:
            required.append(p.name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


class AbstractBlackholeTools(ABC):
    """
    Base class for vendor-specific Blackhole tool adapters.

    Subclasses implement:
      - ``definitions()``  → whatever the vendor expects in their API call
      - ``handle(call)``   → execute a tool call and return the vendor result format
    """

    def __init__(self, blackhole: Blackhole) -> None:
        self._bh = blackhole

    @abstractmethod
    def definitions(self) -> list[Any]:
        """Return tool definitions in the vendor's native schema format."""
        ...

    @abstractmethod
    async def handle(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        """
        Execute a single tool call.

        Parameters
        ----------
        tool_name:
            One of the ``blackhole_*`` names.
        tool_input:
            The parsed input dict as provided by the LLM.

        Returns
        -------
        The result in whatever format the vendor expects for tool results.
        """
        ...

    # ------------------------------------------------------------------
    # Shared dispatch & operation logic
    # ------------------------------------------------------------------

    async def _dispatch(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> dict[str, Any]:
        match tool_name:
            case "blackhole_put":
                return await self._put(tool_input)
            case "blackhole_get":
                return await self._get(tool_input)
            case "blackhole_exists":
                return await self._exists(tool_input)
            case "blackhole_delete":
                return await self._delete(tool_input)
            case _:
                raise ValueError(f"Unhandled tool: {tool_name!r}")

    async def _put(self, inp: dict[str, Any]) -> dict[str, Any]:
        path = Path(inp["file_path"]).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"No such file: {path}")

        filename: str = inp.get("filename") or path.name
        content_type: str | None = (
            inp.get("content_type") or mimetypes.guess_type(str(path))[0]
        )

        stored_filename = await self._bh.put(str(path), filename=filename)
        return {
            "filename": stored_filename,
            "size": path.stat().st_size,
            "content_type": content_type,
        }

    async def _get(self, inp: dict[str, Any]) -> dict[str, Any]:
        filename: str = inp["filename"]
        bh_file = await self._bh.get(filename)

        suffix = Path(bh_file.filename).suffix or ""
        tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix="blackhole_"
        )
        tmp.write(bh_file.blob)
        tmp.close()

        return {
            "filename": bh_file.filename,
            "content_type": bh_file.content_type,
            "size": bh_file.size,
            "file_path": tmp.name,
        }

    async def _exists(self, inp: dict[str, Any]) -> dict[str, Any]:
        filename: str = inp["filename"]
        exists = await self._bh.exists(filename)
        return {"filename": filename, "exists": exists}

    async def _delete(self, inp: dict[str, Any]) -> dict[str, Any]:
        filename: str = inp["filename"]
        await self._bh.delete(filename)
        return {"filename": filename, "deleted": True}
