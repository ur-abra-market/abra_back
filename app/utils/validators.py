from fastapi.datastructures import UploadFile
from starlette import status

from core.exceptions import UnprocessableEntityException
from core.settings import upload_file_settings


def validate_image(
    file: UploadFile,
    max_size: int = upload_file_settings.IMAGE_SIZE_LIMIT_MB * 1024 * 1024,
) -> None:
    if not any(
        [
            valid_type in file.content_type
            for valid_type in upload_file_settings.IMAGE_CONTENT_TYPE_LIMIT
        ]
    ):
        raise UnprocessableEntityException(detail="Unsupported image format")
    if file.size > max_size:
        raise UnprocessableEntityException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size is too big. Limit is {upload_file_settings.IMAGE_SIZE_LIMIT_MB}mb",
        )
