from __future__ import annotations

from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, types
from sqlalchemy.orm import mapped_column

bool_true = Annotated[bool, mapped_column(types.Boolean, default=True)]
datetime_timezone = Annotated[datetime, mapped_column(types.DateTime(timezone=True))]
decimal_10_2 = Annotated[float, 10, 2]
decimal_3_2 = Annotated[float, 3, 2]
decimal_2_1 = Annotated[float, 2, 1]
str_200 = Annotated[str, 200]  # for email use
str_100 = Annotated[str, 100]
str_50 = Annotated[str, 50]
str_36 = Annotated[str, 36]
str_30 = Annotated[str, 30]
str_25 = Annotated[str, 25]
str_20 = Annotated[str, 20]
str_16 = Annotated[str, 16]
str_15 = Annotated[str, 15]

category_id_fk = Annotated[int, mapped_column(ForeignKey("category.id"))]
category_property_type_fk = Annotated[int, mapped_column(ForeignKey("categorypropertytype.id"))]
category_property_value_fk = Annotated[int, mapped_column(ForeignKey("categorypropertyvalue.id"))]
category_variation_type_fk = Annotated[int, mapped_column(ForeignKey("categoryvariationtype.id"))]
category_variation_value_fk = Annotated[
    int, mapped_column(ForeignKey("categoryvariationvalue.id"))
]
company_id_fk = Annotated[int, mapped_column(ForeignKey("company.id"))]
order_id_fk = Annotated[int, mapped_column(ForeignKey("order.id"))]
order_status_fk = Annotated[int, mapped_column(ForeignKey("orderstatus.id"))]
order_product_variation_fk = Annotated[int, mapped_column(ForeignKey("orderproductvariation.id"))]
product_variation_count_fk = Annotated[int, mapped_column(ForeignKey("productvariationcount.id"))]
product_variation_value_fk = Annotated[int, mapped_column(ForeignKey("productvariationvalue.id"))]
product_id_fk = Annotated[int, mapped_column(ForeignKey("product.id"))]
product_review_id_fk = Annotated[int, mapped_column(ForeignKey("productreview.id"))]
seller_id_fk = Annotated[int, mapped_column(ForeignKey("seller.id"))]
supplier_id_fk = Annotated[int, mapped_column(ForeignKey("supplier.id"))]
user_id_fk = Annotated[int, mapped_column(ForeignKey("user.id"))]
