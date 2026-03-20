from typing import Any

from blackhole_io.store.abstract import AbstractStore


def create_store(store_config: dict[str, Any]) -> AbstractStore:
    store_type = store_config.get("type")
    if store_type == "sql":
        from blackhole_io.store.sql_store import SQLStore

        engine = store_config.get("engine")
        dsn = store_config.get("dsn")
        return SQLStore(engine=engine, dsn=dsn)

    raise ValueError(
        f"Unknown store type '{store_type}'. Supported types: sql"
    )
