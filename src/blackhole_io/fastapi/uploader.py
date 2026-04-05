from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.datastructures import UploadFile
from fastapi import Request, UploadFile

if TYPE_CHECKING:
    from blackhole_io import Blackhole


class Uploader:
    def __init__(self, blackhole: Blackhole) -> None:
        self.blackhole = blackhole

    async def __call__(self, request: Request):
        form = await request.form()
        print(list(form.keys()))
        file = form["file"]
        print(repr(file))
        # await uploader.blackhole.put(file)
        return file.headers

        # form = await request.form()
        # file = form["file"]
        # await self.blackhole.put(file)
        # return file
