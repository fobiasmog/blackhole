# Blackhole
*ActiveStorage, but for Python*

The universal file storage adapter for the major Cloud storage services like AWS S3, Google Cloud, Azure but also can be used for the local storage. Optionally persists file records in a SQL database via SQLModel.


### TODOs
- [ ] aws, gcp and azure providers
  - [x] local
  - [x] aws
  - [ ] gcp
  - [ ] azure
  - [ ] minio
- [x] aiofiles for local adapter
- [x] tests
- [x] get settings from yaml file (pydantic-settings)
- [x] SQLModel / SQL database integration
  - [ ] save adapter type when storing record
  - [ ] store file's hashsum
  - [ ] use ETag as hashsum and make uniq constraint on that column (create it as well)
  - [ ] remove filename unique constraint
  - [ ] migrations for further schema changes
- [x] pluggable store abstraction (SQL, extensible to Redis, MongoDB, etc.)
- [ ] middlewares (pre/post)
- [ ] put_later - background job uploading/downloading
- [ ] asset management web interface
- [ ] monitoring
- [ ] error tracking
- [x] logging
- [ ] big files upload/download (streaming)
- [ ] ...


### Installation

```bash
# core only
pip install blackhole-io

# with SQL store support (SQLModel + asyncpg + aiosqlite)
pip install "blackhole-io[sql]"

# with CLI
pip install "blackhole-io[cli]"

# everything
pip install "blackhole-io[sql,cli]"
```


### Init

```python
from blackhole_io import Blackhole
from blackhole_io.configs.s3 import S3Config

config = S3Config(
    access_key="...",
    secret_key="...",
    region="us-east-1",
    bucket="...",
)
bh = Blackhole(config=config)
```


### File operations

```python
file = ... # str path | bytes | BytesIO | starlette UploadFile

filename = await bh.put(file)

if await bh.exists(filename):
    bh_file = await bh.get(filename)
    print(bh_file.filename)
    print(bh_file.blob)  # bytes

    await bh.delete(filename)
```


### SQL store — persist a record on every upload

Pass an existing async engine (reuse your app's connection pool) or a DSN to let Blackhole create one:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from blackhole_io import Blackhole
from blackhole_io.store.sql_store import SQLStore

# reuse existing engine
store = SQLStore(engine=existing_engine)

# or create from DSN
store = SQLStore(dsn="postgresql+asyncpg://user:pass@localhost/mydb")

bh = Blackhole(config=config, store=store)

# uploads the file AND inserts a FileRecord row
filename = await bh.put(upload_file, extra_metadata={"user_id": 42})
```

`FileRecord` table (`blackhole_files`):

| column | type |
|---|---|
| id | integer PK |
| filename | text unique |
| content_type | text |
| size | integer |
| created_at | datetime |
| extra_metadata | JSON |

Query records directly:

```python
record = await store.get(filename)
print(record.extra_metadata)

await store.delete(filename)
```


### Store via YAML config

Add a `store` section to `config/blackhole.yaml` — no code changes needed:

```yaml
adapter: local
directory: /tmp/uploads

store:
  type: sql
  dsn: sqlite+aiosqlite:///blackhole.db
```

```python
bh = Blackhole()  # auto-discovers config/blackhole.yaml including the store
```


### Create tables (CLI)

```bash
# from DSN
blackhole create-tables --dsn postgresql+asyncpg://user:pass@localhost/mydb

# from YAML config
blackhole create-tables --config config/blackhole.yaml
```


### FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile
from sqlalchemy.ext.asyncio import create_async_engine
from blackhole_io import Blackhole
from blackhole_io.store.sql_store import SQLStore

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/mydb")
store = SQLStore(engine=engine)
bh = Blackhole(config=config, store=store)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.create_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload/")
async def upload(files: list[UploadFile]):
    filenames = await bh.put_all(files)
    return {"filenames": filenames}
```


### Custom store backend

Implement `AbstractStore` to use any backend (Redis, MongoDB, etc.):

```python
from blackhole_io.store.abstract import AbstractStore
from blackhole_io.store.models import FileRecord, FileRecordInput

class RedisStore(AbstractStore):
    async def save(self, record: FileRecordInput) -> FileRecord: ...
    async def get(self, filename: str) -> FileRecord | None: ...
    async def delete(self, filename: str) -> None: ...
    async def create_tables(self) -> None: ...  # no-op for Redis

bh = Blackhole(config=config, store=RedisStore(...))
```
