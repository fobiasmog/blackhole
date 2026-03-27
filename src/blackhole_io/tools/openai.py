"""
OpenAI Agent SDK tool adapter for Blackhole.

Usage
-----
::

    from agents import Agent, Runner
    from blackhole_io import Blackhole
    from blackhole_io.configs.s3 import S3Config
    from blackhole_io.tools.openai import BlackholeOpenAITools

    bh = Blackhole(config=S3Config(...))
    bh_tools = BlackholeOpenAITools(bh)

    agent = Agent(
        name="File Manager",
        instructions="You help users manage files using Blackhole storage.",
        tools=bh_tools.definitions(),
    )

    result = await Runner.run(agent, "Upload /tmp/report.pdf for me.")
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from blackhole_io.tools.base import (OPERATION_MAP, OPERATIONS,
                                     AbstractBlackholeTools, build_json_schema)

if TYPE_CHECKING:
    from blackhole_io import Blackhole


class BlackholeOpenAITools(AbstractBlackholeTools):
    """
    OpenAI Agent SDK adapter for a ``Blackhole`` instance.

    Exposes four tools as ``FunctionTool`` instances compatible with
    the ``agents`` package (``openai-agents``):
    - ``blackhole_put``    - upload a file from a local path
    - ``blackhole_get``    - download a file (writes to temp file, returns path + metadata)
    - ``blackhole_exists`` - check whether a file exists
    - ``blackhole_delete`` - permanently delete a file

    Parameters
    ----------
    blackhole:
        An initialised ``Blackhole`` instance.
    """

    def __init__(self, blackhole: Blackhole) -> None:
        super().__init__(blackhole)

    def definitions(self) -> list[Any]:
        """
        Return a list of ``FunctionTool`` instances ready to pass as
        ``tools=[...]`` when creating an ``Agent``.
        """
        from agents import FunctionTool  # lazy import — optional dependency

        tools: list[Any] = []
        for op in OPERATIONS:

            async def _invoke(
                ctx: Any, args_json: str, *, _op_name: str = op.name
            ) -> str:
                tool_input = json.loads(args_json)
                return await self.handle(_op_name, tool_input)

            tools.append(
                FunctionTool(
                    name=op.name,
                    description=op.description,
                    params_json_schema=build_json_schema(op.params),
                    on_invoke_tool=_invoke,
                )
            )
        return tools

    async def handle(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> str:
        """
        Execute a single tool call and return a JSON string result.

        This is the format expected by the OpenAI Agent SDK's
        ``FunctionTool.on_invoke_tool`` callback.

        Parameters
        ----------
        tool_name:
            The tool name (one of the ``blackhole_*`` names).
        tool_input:
            The parsed input dict.

        Returns
        -------
        A JSON-encoded string with the operation result or an error dict.
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

        return json.dumps(result)
