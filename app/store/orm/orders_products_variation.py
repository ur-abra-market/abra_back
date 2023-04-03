from __future__ import annotations

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from orm import OrderModel
from orm import OrderProductVariationModel as Model
from orm import ProductVariationCountModel as CountModel
from orm import ProductVariationValueModel as ValueModel

from .accessor import ORMAccessor


class OrdersProductsVariation(ORMAccessor[Model]):
    def __init__(self) -> None:
        super(OrdersProductsVariation, self).__init__(Model)

    async def is_allowed(self, session: AsyncSession, product_id: int, seller_id: int) -> bool:
        result = await self.get_one(
            session=session,
            join=[
                (
                    OrderModel,
                    and_(
                        OrderModel.id == Model.order_id,
                        OrderModel.seller_id == seller_id,
                        Model.status_id == 0,
                    ),
                ),
                (CountModel, CountModel.id == Model.product_variation_count_id),
                (
                    ValueModel,
                    and_(
                        or_(
                            ValueModel.id == CountModel.product_variation_value1_id,
                            ValueModel.id == CountModel.product_variation_value2_id,
                        ),
                        ValueModel.product_id == product_id,
                    ),
                ),
            ],
        )

        return bool(result)
