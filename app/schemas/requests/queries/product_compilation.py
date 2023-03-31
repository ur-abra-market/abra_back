from enums import SortType

from ...schema import ApplicationSchema


class ProductCompilation(ApplicationSchema):
    category_id: int = None
    order_by: SortType = None
