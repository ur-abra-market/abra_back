from fastapi import APIRouter
from fastapi.param_functions import Path
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core import exceptions
from core.depends import DatabaseSession, SellerAuthorization
from enums import OrderStatus as OrderStatusEnum
from orm import OrderModel, OrderStatusHistoryModel, OrderStatusModel
from schemas import ApplicationResponse, OrderStatus
from typing_ import RouteReturnT

router = APIRouter()


async def create_order_core(
    order_id: int,
    seller_id: int,
    session: AsyncSession,
) -> None:
    order = (
        (
            await session.execute(
                select(OrderModel).where(
                    OrderModel.id == order_id,
                    OrderModel.seller_id == seller_id,
                    OrderModel.is_cart.is_(True),
                )
            )
        )
        .scalars()
        .unique()
        .one_or_none()
    )

    if not order or not order.is_cart:
        raise exceptions.BadRequestException(
            detail="Specified invalid order id",
        )

    # delete order from cart
    order.is_cart = False

    await session.execute(
        insert(OrderStatusHistoryModel).values(
            {
                OrderStatusHistoryModel.order_id: order.id,
                OrderStatusHistoryModel.order_status_id: (
                    select(OrderStatusModel.id)
                    .where(OrderStatusModel.name == OrderStatusEnum.PENDING.value)
                    .scalar_subquery()
                ),
            }
        )
    )


@router.post(
    path="/{order_id}/create",
    description="Turn cart into order (after successful payment)",
    summary="WORKS: create order from a cart.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def create_order(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
) -> RouteReturnT:
    await create_order_core(order_id=order_id, seller_id=user.seller.id, session=session)

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/{order_id}/status",
    summary="WORKS: returns order status",
    response_model=ApplicationResponse[OrderStatus],
    status_code=status.HTTP_200_OK,
)
async def get_order_status(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
) -> RouteReturnT:
    order = (
        (
            await session.execute(
                select(OrderStatusHistoryModel)
                .join(OrderModel)
                .where(
                    OrderStatusHistoryModel.order_id == order_id,
                    OrderModel.seller_id == user.seller.id,
                )
                .options(joinedload(OrderStatusHistoryModel.status))
                .order_by(OrderStatusHistoryModel.created_at.desc())
                .limit(1)
            )
        )
        .scalars()
        .one_or_none()
    )

    if not order:
        raise exceptions.NotFoundException(detail="Order not found")

    return {
        "ok": True,
        "result": order.status,
    }
