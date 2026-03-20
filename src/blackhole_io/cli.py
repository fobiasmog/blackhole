import asyncio
from typing import Optional

import typer

app = typer.Typer(name="blackhole", help="Blackhole CLI")


def _run(coro):
    asyncio.run(coro)


@app.command("create-tables")
def create_tables(
    dsn: Optional[str] = typer.Option(None, "--dsn", help="Database DSN string"),
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to blackhole YAML config file"
    ),
):
    """Create database tables for the configured store."""
    from blackhole_io.store.sql_store import SQLStore

    store: Optional[object] = None

    if config is not None:
        from blackhole_io.configs.loader import load_config_with_store

        _, store = load_config_with_store(config)
        if store is None:
            typer.echo(
                "No store section found in config. Add a 'store' key to your YAML.",
                err=True,
            )
            raise typer.Exit(code=1)
    elif dsn is not None:
        store = SQLStore(dsn=dsn)
    else:
        typer.echo("Provide --dsn or --config.", err=True)
        raise typer.Exit(code=1)

    async def _create():
        await store.create_tables()
        typer.echo("Tables created successfully.")

    _run(_create())
