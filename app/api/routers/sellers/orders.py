from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi.param_functions import Path
from sqlalchemy import desc, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from core import exceptions
from core.depends import DatabaseSession, SellerAuthorization
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    SellerModel,
    product,
)
from schemas import ApplicationResponse, Order, OrderHistory, OrderStatus
from schemas.uploads import PaginationUpload
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

    if not order:
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


@router.get(
    path="/history",
    summary="Return seller's orders history",
    response_model=ApplicationResponse[List[OrderHistory]],
    status_code=status.HTTP_200_OK,
)
async def get_orders_history(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_status_id: Optional[int] = None,
    pagination: PaginationUpload = Depends(),
) -> RouteReturnT:
    query = (
        select(OrderModel)
        .where(OrderModel.seller_id == user.seller.id)
        .options(
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .options(
                selectinload(BundleVariationPodModel.prices),
                selectinload(BundleVariationPodModel.product).selectinload(
                    product.ProductModel.images
                ),
            ),
            selectinload(OrderModel.seller).contains_eager(SellerModel.user),
        )
        .order_by(desc(OrderModel.created_at))
        .distinct()
    )

    # Apply filter by order status id
    if order_status_id:
        max_order_status_history_subquery = (
            select(OrderStatusHistoryModel.order_id)
            .having(func.max(OrderStatusHistoryModel.order_status_id) == order_status_id)
            .group_by(OrderStatusHistoryModel.order_id)
            .subquery()
        )

        query = query.filter(
            OrderModel.id.in_(
                select(max_order_status_history_subquery.c.order_id).select_from(
                    max_order_status_history_subquery
                )
            )
        )

    query = query.offset(pagination.offset).limit(pagination.limit)

    orders_data = (await session.execute(query)).scalars().all()

    # Accumulate total price for each order
    for order in orders_data:
        total_order_price = 0
        for detail in order.details:
            bundle_variation_pod = detail.bundle_variation_pod
            if bundle_variation_pod:
                for bundle_variation_pod_price in bundle_variation_pod.prices:
                    total_order_price += bundle_variation_pod_price.value
        order.total_order_price = total_order_price

    return {"ok": True, "result": orders_data}


@router.get(
    path="/statuses",
    summary="Return order statuses",
    response_model=ApplicationResponse[List[OrderStatus]],
    status_code=status.HTTP_200_OK,
)
async def get_order_statuses(
    session: DatabaseSession,
) -> RouteReturnT:
    orders_statuses = (await session.execute(select(OrderStatusModel))).scalars().all()

    return {"ok": True, "result": orders_statuses}


@router.post(
    path="/",
    summary="Get orders by id for checkout page",
    response_model=ApplicationResponse[List[Order]],
    status_code=status.HTTP_200_OK,
)
async def get_orders_by_ids(
    ids: List[int],
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    query = select(OrderModel).where(
        OrderModel.seller_id == user.seller.id,
        OrderModel.is_cart.is_(True),
        OrderModel.id.in_(ids),
    )
    orders = (await session.execute(query)).scalars().all()

    return orders
