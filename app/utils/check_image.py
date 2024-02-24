from io import BytesIO
from PIL import Image

from core.settings import upload_file_settings
from core.exceptions import BadRequestException


def check_image(byte_date: bytes, field_name: str, field_data: str):
    checking_binary_image_type(byte_date, field_name, field_data)
    checking_binary_image_for_equal_sides(byte_date, field_name, field_data)
    
    
def checking_binary_image_type(byte_date: bytes, field_name: str, field_data: str):
    format_image = Image.open(BytesIO(byte_date)).format
    if not format_image in upload_file_settings.ALLOWED_IMAGE_TYPES:
        raise BadRequestException(detail=f"Invalid image type. Data:{field_name}={field_data}")
    

def checking_binary_image_for_equal_sides(byte_date: bytes, field_name: str, field_data: str):
    size_image = Image.open(BytesIO(byte_date)).size
    if size_image[0] != size_image[1]:
        raise BadRequestException(detail=f"The image is not square. Data: {field_name}={field_data}")