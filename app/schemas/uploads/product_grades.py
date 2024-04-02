from typing import Optional

from ..schema import ApplicationSchema


class ProductGradesUpload(ApplicationSchema):
    grade: Optional[int] = None
    with_photos: Optional[bool] = None
