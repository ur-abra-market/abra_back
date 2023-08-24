from __future__ import annotations

from datetime import datetime

import pytz
from sqlalchemy import ForeignKey
from sqlalchemy import text as t
from sqlalchemy import types
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

bool_no_value = Annotated[bool, mapped_column(types.Boolean)]
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

decimal_10_2 = Annotated[float, mapped_column(types.DECIMAL(10, 2))]
decimal_3_2 = Annotated[float, mapped_column(types.DECIMAL(3, 2))]
decimal_2_1 = Annotated[float, mapped_column(types.DECIMAL(2, 1))]

small_int = Annotated[int, mapped_column(types.SMALLINT, nullable=False, server_default=t("1"))]
big_int = Annotated[int, mapped_column(types.BIGINT)]
int = Annotated[int, mapped_column(types.INTEGER)]

str_200 = Annotated[str, mapped_column(types.String(200))]  # for email use
str_100 = Annotated[str, mapped_column(types.String(100))]
str_50 = Annotated[str, mapped_column(types.String(50))]
str_36 = Annotated[str, mapped_column(types.String(36))]
str_30 = Annotated[str, mapped_column(types.String(30))]
str_25 = Annotated[str, mapped_column(types.String(25))]
str_20 = Annotated[str, mapped_column(types.String(20))]
str_16 = Annotated[str, mapped_column(types.String(16))]
str_15 = Annotated[str, mapped_column(types.String(15))]
str_14 = Annotated[str, mapped_column(types.String(14))]
str_4 = Annotated[str, mapped_column(types.String(4))]
text = Annotated[str, mapped_column(types.Text)]

bundle_id_fk = Annotated[int, mapped_column(ForeignKey("bundle.id"))]
category_id_fk = Annotated[int, mapped_column(ForeignKey("category.id"))]
property_type_fk = Annotated[int, mapped_column(ForeignKey("property_type.id"))]
property_value_fk = Annotated[int, mapped_column(ForeignKey("property_value.id"))]
variation_type_fk = Annotated[int, mapped_column(ForeignKey("variation_type.id"))]
variation_value_fk = Annotated[int, mapped_column(ForeignKey("variation_value.id"))]
company_id_fk = Annotated[int, mapped_column(ForeignKey("company.id"))]
country_id_fk = Annotated[int, mapped_column(ForeignKey("country.id"))]
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
seller_address_fk = Annotated[int, mapped_column(ForeignKey("seller_address.id"))]
seller_id_fk = Annotated[int, mapped_column(ForeignKey("seller.id"))]
supplier_id_fk = Annotated[int, mapped_column(ForeignKey("supplier.id"))]
user_id_fk = Annotated[int, mapped_column(ForeignKey("user.id"))]
variation_value_to_product_fk = Annotated[
    int, mapped_column(ForeignKey("variation_value_to_product.id"))
]
