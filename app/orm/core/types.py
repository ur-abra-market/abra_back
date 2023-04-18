from __future__ import annotations

from datetime import datetime

try:
    from typing_extensions import Annotated
except ImportError:
    from typing_extensions import Annotated

import pytz
from sqlalchemy import ForeignKey, text, types
from sqlalchemy.orm import mapped_column

__all__ = (
    "bool_false",
    "bool_true",
    "category_id_fk",
    "category_property_type_fk",
    "category_property_value_fk",
    "category_variation_type_fk",
    "category_variation_value_fk",
    "company_id_fk",
    "datetime_timezone",
    "decimal_2_1",
    "decimal_3_2",
    "decimal_10_2",
    "order_id_fk",
    "order_product_variation_fk",
    "order_status_fk",
    "product_id_fk",
    "product_review_id_fk",
    "product_variation_count_fk",
    "product_variation_value_fk",
    "seller_id_fk",
    "str_4",
    "str_14",
    "str_15",
    "str_16",
    "str_20",
    "str_25",
    "str_30",
    "str_36",
    "str_50",
    "str_100",
    "str_200",
    "small_int",
    "text",
    "moscow_datetime_timezone",
    "supplier_id_fk",
    "user_id_fk",
)

bool_false = Annotated[bool, mapped_column(types.Boolean, default=False, nullable=True)]
bool_true = Annotated[bool, mapped_column(types.Boolean, default=True, nullable=True)]
datetime_timezone = Annotated[datetime, mapped_column(types.DateTime(timezone=True))]
moscow_datetime_timezone = Annotated[
    datetime,
    mapped_column(
        default=datetime.now(tz=pytz.timezone("Europe/Moscow")),
        type_=types.TIMESTAMP(timezone=True),
    ),
]
decimal_10_2 = Annotated[float, 10, 2]
decimal_3_2 = Annotated[float, 3, 2]
decimal_2_1 = Annotated[float, 2, 1]
small_int = Annotated[int, mapped_column(types.SMALLINT, nullable=False, server_default=text("1"))]
str_200 = Annotated[str, 200]  # for email use
str_100 = Annotated[str, 100]
str_50 = Annotated[str, 50]
str_36 = Annotated[str, 36]
str_30 = Annotated[str, 30]
str_25 = Annotated[str, 25]
str_20 = Annotated[str, 20]
str_16 = Annotated[str, 16]
str_15 = Annotated[str, 15]
str_14 = Annotated[str, 14]
str_4 = Annotated[str, 4]
text = Annotated[str, mapped_column(types.Text)]

category_id_fk = Annotated[int, mapped_column(ForeignKey("category.id"))]
category_property_type_fk = Annotated[int, mapped_column(ForeignKey("category_property_type.id"))]
category_property_value_fk = Annotated[
    int, mapped_column(ForeignKey("category_property_value.id"))
]
category_variation_type_fk = Annotated[
    int, mapped_column(ForeignKey("category_variation_type.id"))
]
category_variation_value_fk = Annotated[
    int, mapped_column(ForeignKey("category_variation_value.id"))
]
company_id_fk = Annotated[int, mapped_column(ForeignKey("company.id"))]
order_id_fk = Annotated[int, mapped_column(ForeignKey("order.id"))]
order_status_fk = Annotated[int, mapped_column(ForeignKey("order_status.id"))]
order_product_variation_fk = Annotated[
    int, mapped_column(ForeignKey("order_product_variation.id"))
]
product_variation_count_fk = Annotated[
    int, mapped_column(ForeignKey("product_variation_count.id"))
]
product_variation_value_fk = Annotated[
    int, mapped_column(ForeignKey("product_variation_value.id"))
]
product_id_fk = Annotated[int, mapped_column(ForeignKey("product.id"))]
product_review_id_fk = Annotated[int, mapped_column(ForeignKey("product_review.id"))]
seller_id_fk = Annotated[int, mapped_column(ForeignKey("seller.id"))]
supplier_id_fk = Annotated[int, mapped_column(ForeignKey("supplier.id"))]
user_id_fk = Annotated[int, mapped_column(ForeignKey("user.id"))]
