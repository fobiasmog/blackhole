import pytest_asyncio

from blackhole_io.adapters.local_adapter import LocalAdapter
from blackhole_io.configs.local import LocalConfig


@pytest_asyncio.fixture
async def adapter(tmp_path):
    config = LocalConfig(directory=str(tmp_path))
    return LocalAdapter(config)
