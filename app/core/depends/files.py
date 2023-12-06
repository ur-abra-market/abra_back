from __future__ import annotations

import imghdr
from dataclasses import dataclass
from typing import Optional

from fastapi.datastructures import UploadFile
from fastapi.param_functions import File

from core.exceptions import BadRequestException, UnprocessableEntityException
from core.settings import upload_file_settings


@dataclass(repr=False, eq=False, frozen=True)
class FileObjects:
    source: UploadFile
    contents: bytes


async def image_required(file: UploadFile = File(...)) -> FileObjects:
    contents = await file.read()
    if len(contents) > upload_file_settings.FILE_SIZE_LIMIT_MB * 1024 * 1024:
        raise BadRequestException(
            detail=f"Exceeded file size limit: {upload_file_settings.FILE_SIZE_LIMIT_MB}Mb"
        )
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
