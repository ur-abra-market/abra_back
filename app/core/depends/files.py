from __future__ import annotations

import imghdr
from dataclasses import dataclass

from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import File
from starlette import status


@dataclass(
    repr=False,
    eq=False,
    frozen=True,
)
class FileObjects:
    source: UploadFile
    contents: bytes


async def image_required(file: UploadFile = File(...)) -> FileObjects:
    contents = await file.read()
    if not imghdr.what(file=file.filename, h=contents):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image in file required",
        )

    await file.seek(0)
    return FileObjects(source=file, contents=contents)
