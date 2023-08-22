from __future__ import annotations

from enums import ProductCompilationSortingEnum

from ..schema import ApplicationSchema


class ProductCompilationSortingUpload(ApplicationSchema):
    sort: ProductCompilationSortingEnum = ProductCompilationSortingEnum.RATING.value
    ascending: bool = False
