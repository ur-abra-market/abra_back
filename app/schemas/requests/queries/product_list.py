from ...schema import ApplicationResponse
from enums import SortType
from queries import QueryPagination


class ProductList(QueryPagination):
    category_id: int = None
    order_by: SortType = None
