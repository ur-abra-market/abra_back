from typing import Sequence

from fastapi import APIRouter
from fastapi.param_functions import Depends, Path, Query
from sqlalchemy import and_, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
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
)
from orm.product import ProductModel
from schemas import ApplicationResponse, Order
from schemas.uploads import StatusDataUpload
from schemas.uploads.order_data import OrderQueryParams
from typing_ import RouteReturnT

router = APIRouter()


async def get_supplier_orders_core(
    supplier_id: int,
    session: AsyncSession,
    query_params: OrderQueryParams,
) -> Sequence[OrderModel]:
    actual_statuses = (
        select(
            OrderStatusHistoryModel.order_id,
            func.max(OrderStatusHistoryModel.created_at).label("last_date"),
        )
        .group_by(OrderStatusHistoryModel.order_id)
        .subquery("actual_statuses")
    )

    result = (
        (
            await session.execute(
                select(OrderModel)
                .join(OrderModel.details)
                .join(BundleVariationPodAmountModel.bundle_variation_pod)
                .join(
                    BundleVariationPodModel.product.and_(
                        ProductModel.supplier_id == supplier_id,
                        ProductModel.name.ilike(f"{query_params.product_name}%"),
                    )
                )
                .join(OrderModel.status_history)
                .join(
                    actual_statuses,
                    and_(
                        OrderStatusHistoryModel.order_id == actual_statuses.c.order_id,
                        OrderStatusHistoryModel.created_at == actual_statuses.c.last_date,
                    ),
                )
                .join(
                    OrderStatusHistoryModel.status.and_(
                        OrderStatusModel.name == query_params.status
                    )
                )
                .options(
                    joinedload(OrderModel.seller),
                    selectinload(OrderModel.details),
                )
                .offset(query_params.offset)
                .limit(query_params.limit)
                .distinct()
            )
        )
        .scalars()
        .all()
    )
    return result


@router.get(
    path="",
    summary="WORKS: Get all supplier orders",
    response_model=ApplicationResponse[list[Order]],
    status_code=status.HTTP_200_OK,
)
async def get_supplier_orders(
    user: SupplierAuthorization,
    session: DatabaseSession,
    query_params: OrderQueryParams = Depends(),
) -> RouteReturnT:
    result = await get_supplier_orders_core(
        supplier_id=user.supplier.id,
        session=session,
        query_params=query_params,
    )

    return {
        "ok": True,
        "result": result,
    }


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


async def accept_order_status_core(
    session: AsyncSession,
    order_id: int,
    supplier_id: int,
) -> None:
    order = (
        (
            await session.execute(
                select(OrderModel)
                .options(selectinload(OrderModel.status_history))
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
            select(OrderStatusModel.id).where(
                OrderStatusModel.name == OrderStatusEnum.ACCEPTED.value
            )
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
    path="/{order_id}/accept",
    summary="WORKS: changes order status to accepted",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def accept_order_status(
    user: SupplierAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
) -> RouteReturnT:
    await accept_order_status_core(
        session=session,
        order_id=order_id,
        supplier_id=user.supplier.id,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.put(
    path="/{order_id}/complete",
    summary="WORKS: changes order status to complete",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def compete_order_status(
    user: SupplierAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
) -> RouteReturnT:
    await change_order_status_core(
        session=session,
        order_id=order_id,
        supplier_id=user.supplier.id,
        status_data=OrderStatusEnum.COMPLETED,
    )

    return {
        "ok": True,
        "result": True,
    }
