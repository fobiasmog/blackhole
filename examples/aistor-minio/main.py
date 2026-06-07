import asyncio
from blackhole_io import Blackhole
from blackhole_io.configs.aistore import AIStoreConfig
import os

async def main():
    config = AIStoreConfig(
        endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    )
    filename = "./test.md"
    bh = Blackhole(config=config)
    result = await bh.put(filename)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
