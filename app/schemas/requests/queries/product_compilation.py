from enums import SortType

from ...schema import ApplicationSchema


class ProductCompilation(ApplicationSchema):
    category_id: int = 0
    order_by: SortType = None
