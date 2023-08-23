from __future__ import annotations

from enums import ProductSortingEnum

from ..schema import ApplicationSchema


class ProductSortingUpload(ApplicationSchema):
    sort: ProductSortingEnum = ProductSortingEnum.RATING.value
    ascending: bool = False
