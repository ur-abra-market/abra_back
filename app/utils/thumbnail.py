from __future__ import annotations

from io import BytesIO

from fastapi.datastructures import UploadFile
from PIL import Image as PILImage

from core.app import aws_s3
from core.depends import FileObjects


def thumbnail(contents: bytes, content_type: str, size: tuple[int, int]) -> BytesIO:
    io = BytesIO()
    image = PILImage.open(BytesIO(contents))
    image.thumbnail(size)
    image.save(io, format=content_type.split("/")[-1])
    io.seek(0)
    return io


def byte_thumbnail(contents: bytes, size: tuple[int, int]) -> BytesIO:
    image = PILImage.open(BytesIO(contents))
    resized_image = image.resize(size)

    output_buffer = BytesIO()
    resized_image.save(output_buffer, format=image.format)
    resized_image_bytes = output_buffer.getvalue()

    return resized_image_bytes


async def upload_thumbnail(file: FileObjects, bucket: str, size: tuple[int, int]) -> str:
    io = thumbnail(contents=file.contents, content_type=file.source.content_type, size=size)
    try:
        thumb_link = await aws_s3.upload_file_to_s3(
            bucket_name=bucket,
            file=FileObjects(
                contents=io.getvalue(),
                source=UploadFile(
                    file=io,
                    size=io.getbuffer().nbytes,
                    filename=file.source.filename,
                    headers=file.source.headers,
                ),
            ),
        )
    except Exception:
        io.close()
        raise

    return thumb_link
