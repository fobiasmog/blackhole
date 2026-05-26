import asyncio
from blackhole_io import Blackhole
from blackhole_io.configs.s3 import AIStorConfig
import os

async def main():
    config = AIStorConfig(
        url=os.getenv("MINIO_URL", "http://localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    )
    filename = "./test.md"
    bh = Blackhole(config=config)
    await bh.put(filename)


if __name__ == "__main__":
    asyncio.run(main())
