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

    img = Image.open(file.file)
    if img.width != img.height:
        raise UnprocessableEntityException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is not square. Image width <{img.width}> & height <{img.height}> are not equal",
        )
