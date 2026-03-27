"""
Full agentic loop example — Blackhole + OpenAI Agent SDK.

Run with:
    OPENAI_API_KEY=... python examples/openai_agent_loop.py
"""

from __future__ import annotations

import asyncio
import argparse
from pathlib import Path
from typing import Optional

from agents import Agent, Runner

from blackhole_io import Blackhole
from blackhole_io.configs.local import LocalConfig
from blackhole_io.configs.s3 import S3Config
from blackhole_io.tools.openai import BlackholeOpenAITools


async def main(storage: Optional[str], bucket: Optional[str], region: Optional[str]) -> None:
    if storage == "s3":
        config = S3Config(
            bucket=bucket,
            region=region,
        )
    else:
        config = LocalConfig(directory="/tmp/blackhole_demo")

    bh = Blackhole(config=config)
    bh_tools = BlackholeOpenAITools(bh)

    agent = Agent(
        name="File Manager",
        instructions=(
            "You help users manage files using Blackhole storage. "
            "Use the blackhole_* tools to upload, download, check, "
            "and delete files."
        ),
        tools=bh_tools.definitions(),
    )

    file_path = input("Enter a file path to upload: ").strip()
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        print(f"Error: '{path}' is not a valid file.")
        return

    result = await Runner.run(
        agent,
        (
            f"Please store the file located at '{path}' for me. "
            f"After uploading, confirm the file exists and tell me its metadata."
        ),
    )
    print(f"[Agent]: {result.final_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Blackhole + OpenAI Agent SDK loop")
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
