from io import BytesIO

from PIL import Image

from core.exceptions import BadRequestException
from core.settings import upload_file_settings


def check_image(byte_date: bytes, field_name: str, field_data: int, order: int):
    image_data = Image.open(BytesIO(byte_date))
    if image_data.format not in upload_file_settings.ALLOWED_IMAGE_TYPES:
        raise BadRequestException(
            detail=f"Invalid image type. Data:{field_name}={field_data}, order={order}"
        )
    if image_data.size[0] != image_data.size[1]:
        raise BadRequestException(
            detail=f"The image is not square. Data:{field_name}={field_data}, order={order}"
        )
