"""
Full agentic loop example — Blackhole + Anthropic tool use.

Run with:
    ANTHROPIC_API_KEY=... python examples/anthropic_agent_loop.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional
import argparse

import anthropic

from blackhole_io import Blackhole
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config
from blackhole_io.tools.anthropic import BlackholeAnthropicTools


async def main(storage: Optional[str], bucket: Optional[str], region: Optional[str]) -> None:
    if storage == 's3':
        config = S3Config(
            bucket=bucket,
            region=region,
        )
    else:
        config = LocalConfig(directory="/tmp/blackhole_demo")

    bh = Blackhole(config=config)
    bh_tools = BlackholeAnthropicTools(bh)
    client = anthropic.AsyncAnthropic()

    file_path = input("Enter a file path to upload: ").strip()
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        print(f"Error: '{path}' is not a valid file.")
        return

    messages: list[dict] = [
        {
            "role": "user",
            "content": (
                f"Please store the file located at '{path}' for me. "
                f"After uploading, confirm the file exists and tell me its metadata."
            ),
        }
    ]

    print("Starting agentic loop...\n")
    while True:
        response = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            tools=bh_tools.definitions(),
            messages=messages,
        )

        for block in response.content:
            if hasattr(block, "text"):
                print(f"[Claude]: {block.text}")

        if response.stop_reason == "end_turn":
            print("\nDone.")
            break

        if response.stop_reason == "tool_use":
            tool_results = await bh_tools.handle_response(response.content)
            for tr in tool_results:
                print(f"[Tool result]: {json.loads(tr['content'])}")
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            print(f"Unexpected stop reason: {response.stop_reason}")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blackhole + Anthropic agent loop")
    parser.add_argument(
        "--storage",
        choices=["local", "s3"],
        default="local",
        help="Storage backend to use (default: local)",
    )
    parser.add_argument(
        "--bucket",
        help="S3 bucket name (required for s3 storage)",
    )
    parser.add_argument(
        "--region",
        help="S3 region (required for s3 storage)",
    )
    args = parser.parse_args()

    asyncio.run(main(storage=args.storage, bucket=args.bucket, region=args.region))
