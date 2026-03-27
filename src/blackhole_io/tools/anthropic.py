"""
Anthropic tool-use adapter for Blackhole.

Usage
-----
::

    import anthropic
    from blackhole_io import Blackhole
    from blackhole_io.configs.s3 import S3Config
    from blackhole_io.tools.anthropic import BlackholeAnthropicTools

    bh = Blackhole(config=S3Config(...))
    bh_tools = BlackholeAnthropicTools(bh)

    client = anthropic.AsyncAnthropic()

    # 1. Pass tool definitions to the API
    response = await client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        tools=bh_tools.definitions(),
        messages=[{"role": "user", "content": "Upload this text: hello world"}],
    )

    # 2. Handle tool calls returned by the model
    for block in response.content:
        if block.type == "tool_use":
            result_block = await bh_tools.handle(block.name, block.input)
            # result_block is a ready-to-send tool_result dict
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from blackhole_io.tools.base import (OPERATION_MAP, OPERATIONS,
                                     AbstractBlackholeTools, build_json_schema)

if TYPE_CHECKING:
    from blackhole_io import Blackhole

# Backward-compatible alias (tests import this directly).
_build_json_schema = build_json_schema


class BlackholeAnthropicTools(AbstractBlackholeTools):
    """
    Anthropic tool-use adapter for a ``Blackhole`` instance.

    Exposes four tools to the model:
    - ``blackhole_put``    - upload a file from a local path
    - ``blackhole_get``    - download a file (writes to temp file, returns path + metadata)
    - ``blackhole_exists`` - check whether a file exists
    - ``blackhole_delete`` - permanently delete a file

    Parameters
    ----------
    blackhole:
        An initialised ``Blackhole`` instance.
    tool_id_prefix:
        Optional prefix for tool_result IDs (useful in multi-agent setups).
    """

    def __init__(self, blackhole: Blackhole, tool_id_prefix: str = "bh") -> None:
        super().__init__(blackhole)
        self._prefix = tool_id_prefix

    def definitions(self) -> list[dict[str, Any]]:
        """
        Return tool definitions ready to pass as ``tools=[...]`` in an
        Anthropic ``messages.create()`` call.
        """
        return [
            {
                "name": op.name,
                "description": op.description,
                "input_schema": build_json_schema(op.params),
            }
            for op in OPERATIONS
        ]

    async def handle(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_use_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a single tool call and return an Anthropic ``tool_result`` block.

        Parameters
        ----------
        tool_name:
            The tool name from the model's ``tool_use`` block.
        tool_input:
            The ``input`` dict from the model's ``tool_use`` block.
        tool_use_id:
            The ``id`` from the model's ``tool_use`` block.

        Returns
        -------
        A dict shaped as an Anthropic ``tool_result`` content block::

            {"type": "tool_result", "tool_use_id": "...", "content": "..."}
        """
        if tool_name not in OPERATION_MAP:
            raise ValueError(
                f"Unknown Blackhole tool: {tool_name!r}. "
                f"Known tools: {list(OPERATION_MAP)}"
            )

        try:
            result = await self._dispatch(tool_name, tool_input)
        except Exception as exc:  # noqa: BLE001
            result = {"error": str(exc)}

        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id or "",
            "content": json.dumps(result),
        }

    async def handle_response(
        self, response_content: list[Any]
    ) -> list[dict[str, Any]]:
        """
        Convenience helper: iterate over all blocks in a model response,
        handle every ``tool_use`` block, and return the list of
        ``tool_result`` blocks to append to your messages.

        Example
        -------
        ::

            response = await client.messages.create(...)
            tool_results = await bh_tools.handle_response(response.content)
            if tool_results:
                follow_up = await client.messages.create(
                    ...,
                    messages=[
                        *previous_messages,
                        {"role": "assistant", "content": response.content},
                        {"role": "user", "content": tool_results},
                    ],
                )
        """
        results: list[dict[str, Any]] = []
        for block in response_content:
            block_type = block.type if hasattr(block, "type") else block.get("type")
            if block_type == "tool_use":
                name = block.name if hasattr(block, "name") else block["name"]
                inp = block.input if hasattr(block, "input") else block["input"]
                uid = block.id if hasattr(block, "id") else block.get("id")
                results.append(await self.handle(name, inp, uid))
        return results
