from fastapi import APIRouter
from fastapi.param_functions import Path, Query
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core import exceptions
from core.depends import DatabaseSession, SupplierAuthorization
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    ProductModel,
)
from schemas import ApplicationResponse
from schemas.uploads import StatusDataUpload
from typing_ import RouteReturnT

router = APIRouter()


async def change_order_status_core(
    session: AsyncSession,
    order_id: int,
    supplier_id: int,
    status_data: StatusDataUpload,
) -> None:
    order = (
        (
            await session.execute(
                select(OrderModel)
                .join(OrderModel.details)
                .join(BundleVariationPodAmountModel.bundle_variation_pod)
                .join(BundleVariationPodModel.product)
                .options(
                    selectinload(OrderModel.details)
                    .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
                    .selectinload(BundleVariationPodModel.product),
                    selectinload(OrderModel.status_history),
                )
                .where(
                    OrderModel.id == order_id,
                    OrderModel.is_cart.is_not(True),
                    ProductModel.supplier_id == supplier_id,
                )
            )
        )
        .scalars()
        .unique()
        .one_or_none()
    )

    if not order:
        raise exceptions.NotFoundException(detail="Order not found")

    order_status_id = (
        await session.execute(
            select(OrderStatusModel.id).where(OrderStatusModel.name == status_data)
        )
    ).scalar_one_or_none()

    if order.status_history[-1].order_status_id == order_status_id:
        raise exceptions.BadRequestException(detail="Order already has that status")

    await session.execute(
        insert(OrderStatusHistoryModel).values(
            {
                OrderStatusHistoryModel.order_id: order_id,
                OrderStatusHistoryModel.order_status_id: order_status_id,
            }
        )
    )


@router.put(
    path="/{order_id}/changeStatus",
    summary="WORKS: changes the status for the ordered product",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_order_status(
    user: SupplierAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
    status: OrderStatusEnum = Query(),
) -> RouteReturnT:
    await change_order_status_core(
        session=session,
        order_id=order_id,
        supplier_id=user.supplier.id,
        status_data=status.value,
    )

    return {
        "ok": True,
        "result": True,
    }
