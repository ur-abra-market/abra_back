from __future__ import annotations

from datetime import datetime

import pytz
from sqlalchemy import text as t
from sqlalchemy import types
from sqlalchemy.orm import mapped_column
from typing_extensions import Annotated

from . import constraints

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

id_pk_type = Annotated[int, constraints.id_pk]

brand_id_fk_type = Annotated[int, constraints.brand_id_fk]
bundle_id_fk_type = Annotated[int, constraints.bundle_id_fk]
bundle_variation_pod_amount_id_fk_type = Annotated[
    int, constraints.bundle_variation_pod_amount_id_fk
]
bundle_variation_pod_id_fk_type = Annotated[int, constraints.bundle_variation_pod_id_fk]
category_id_fk_type = Annotated[int, constraints.category_id_fk]
employees_number_id_fk_type = Annotated[int, constraints.employees_number_id_fk]
property_type_fk_type = Annotated[int, constraints.property_type_fk]
property_value_fk_type = Annotated[int, constraints.property_value_fk]
variation_type_fk_type = Annotated[int, constraints.variation_type_fk]
variation_value_fk_type = Annotated[int, constraints.variation_value_fk]
company_id_fk_type = Annotated[int, constraints.company_id_fk]
country_id_fk_type = Annotated[int, constraints.country_id_fk]
order_id_fk_type = Annotated[int, constraints.order_id_fk]
order_status_fk_type = Annotated[int, constraints.order_status_fk]
order_product_variation_fk_type = Annotated[int, constraints.order_product_variation_fk]
product_variation_count_fk_type = Annotated[int, constraints.product_variation_count_fk]
product_variation_value_fk_type = Annotated[int, constraints.product_variation_value_fk]
product_id_fk_type = Annotated[int, constraints.product_id_fk]
product_review_id_fk_type = Annotated[int, constraints.product_review_id_fk]
seller_address_fk_type = Annotated[int, constraints.seller_address_fk]
seller_id_fk_type = Annotated[int, constraints.seller_id_fk]
supplier_id_fk_type = Annotated[int, constraints.supplier_id_fk]
tag_id_fk_type = Annotated[int, constraints.tag_id_fk]
user_id_fk_type = Annotated[int, constraints.user_id_fk]
variation_value_to_product_fk_type = Annotated[int, constraints.variation_value_to_product_fk]
