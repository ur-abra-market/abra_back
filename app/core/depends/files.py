from __future__ import annotations

import imghdr
from dataclasses import dataclass
from typing import Optional

from fastapi.datastructures import UploadFile
from fastapi.param_functions import File

from core.exceptions import UnprocessableEntityException
from utils.validators import validate_image_size


@dataclass(repr=False, eq=False, frozen=True)
class FileObjects:
    source: UploadFile
    contents: bytes


async def image_required(file: UploadFile = File(...)) -> FileObjects:
    contents = await file.read()
    validate_image_size(contents=contents)
    if not imghdr.what(file=file.filename, h=contents):
        raise UnprocessableEntityException(
            detail="Image in file required",
        )

    await file.seek(0)
    return FileObjects(source=file, contents=contents)


async def image_optional(file: Optional[UploadFile] = File(None)) -> Optional[FileObjects]:
    if not file:
        return None

    return await image_required(file=file)
