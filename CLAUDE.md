# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make format        # Format with isort + ruff

# Run a single test file
pytest tests/test_local_adapter.py -v

# Run a single test
pytest tests/test_local_adapter.py::test_put -v
```

The project uses `uv` for package management. Python 3.13+ is required.

## Architecture

**Blackhole** is an async-first, universal file storage abstraction (inspired by Rails ActiveStorage). It provides a unified API over local filesystem, AWS S3, and GCP Cloud Storage.

### Core flow

```
Blackhole (facade)
  └── AbstractAdapter (strategy pattern)
        ├── LocalAdapter   — aiofiles for true async I/O
        ├── S3Adapter      — boto3 wrapped in run_in_executor
        └── GCPAdapter     — stub, not implemented
```

`AdapterFactory.create()` uses `@overload` typed signatures to return the concrete adapter type based on the config type passed in. All adapters share the same async interface: `put()`, `put_all()`, `get()`, `exists()`, `delete()`.

### Configuration

Configs inherit from `pydantic-settings` `BaseSettings` with environment variable prefixes:
- `LocalConfig` → `BLACKHOLE_LOCAL_*`
- `S3Config` → `BLACKHOLE_S3_*`
- `GCPConfig` → `BLACKHOLE_GCP_*`

`load_config()` in `configs/loader.py` currently only accepts pre-constructed config objects. YAML/env file loading is not yet implemented.

### Input types

All adapter `put()` methods accept `UploadFileType = str | bytes | BytesIO | starlette.UploadFile`.

### Data model

`BlackholeFile` (Pydantic model) is returned from `get()`: fields are `filename`, `content_type`, `size`, `data` (bytes). `.blob` is an alias for `.data`.

### Testing conventions

- Use `pytest-asyncio` with `@pytest.mark.asyncio`
- Use `@pytest_asyncio.fixture` for async fixtures
- `LocalAdapter` tests use `tmp_path` (real filesystem)
- `S3Adapter` tests mock `boto3` entirely
