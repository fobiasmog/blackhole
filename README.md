# Blackhole
*ActiveStorage, but for Python*

The universal file storage adapter for the major Cloud storage services like AWS S3, Google Cloud, Azure but also can be used for the local storage.


### TODOs
[ ] aws, gcp and azure providers
[ ] aiofiles for local adapter
[ ] tests
[ ] get settings from yaml file (pydantic-settings)
[ ] middlewares (pre/post)
[ ] put_later - background job uploading/downloading
[ ] ...


### Init
```python
config = S3Config(
    access_key="...",
    secret_key="...",
    region="us-east-1",
    bucket="...",
)
bh = Blackhole(config=config)
```


### Save
```python
file = ... # some BinaryIO / bytes / file path string

storage_file = storage.put(file)

if storage.exists(file):
    storage.delete(file)

bh_file = storage.get(file)

print(bh_file.filename)

return bh_file.blob #  returns bytes
```


### FastApi
```python
config = ...
bh = Blackhole(config)

@app.post("/uploadfiles/")
async def create_upload_file(files: list[UploadFile]):
    filenames = await bh.put(files)
    return {"filename": filenames}

```
