from fastapi.datastructures import UploadFile
from PIL import Image
from starlette import status

from core.exceptions import UnprocessableEntityException
from core.settings import upload_file_settings


def validate_image(
    file: UploadFile, max_size: int = upload_file_settings.FILE_SIZE_LIMIT_MB * 1024 * 1024
) -> None:
    if file.size > max_size:
        raise UnprocessableEntityException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size is too big. Limit is {upload_file_settings.FILE_SIZE_LIMIT_MB}mb",
        )

    with Image.open(file.file) as img:
        if img.width != img.height:
            raise UnprocessableEntityException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image should be a square, got ({img.width}x{img.height})",
            )
