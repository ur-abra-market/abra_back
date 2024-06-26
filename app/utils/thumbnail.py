from __future__ import annotations

from io import BytesIO

from fastapi.datastructures import UploadFile
from PIL import Image as PILImage

from core.app import aws_s3
from core.depends import FileObjects
from core.settings import aws_s3_settings, user_settings


def thumbnail(contents: bytes, content_type: str) -> BytesIO:
    io = BytesIO()
    image = PILImage.open(BytesIO(contents))
    image.thumbnail((user_settings.USER_LOGO_THUMBNAIL_X, user_settings.USER_LOGO_THUMBNAIL_Y))
    image.save(io, format=content_type.split("/")[-1])
    io.seek(0)
    return io


async def upload_thumbnail(file: FileObjects) -> str:
    io = thumbnail(contents=file.contents, content_type=file.source.content_type)
    try:
        thumb_link = await aws_s3.upload_file_to_s3(
            bucket_name=aws_s3_settings.AWS_S3_IMAGE_USER_LOGO_BUCKET,
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
