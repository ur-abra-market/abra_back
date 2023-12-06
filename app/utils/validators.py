from starlette import status

from core.exceptions import UnprocessableEntityException
from core.settings import upload_file_settings


def validate_image_size(
    contents: bytes, max_size: int = upload_file_settings.FILE_SIZE_LIMIT_MB * 1024 * 1024
) -> None:
    if len(contents) > max_size:
        raise UnprocessableEntityException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size is too big. Limit is {upload_file_settings.FILE_SIZE_LIMIT_MB}mb",
        )
