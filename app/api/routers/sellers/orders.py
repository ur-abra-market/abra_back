from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends
from fastapi.param_functions import Path
from sqlalchemy import and_, desc, func, insert, select, update
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
    SupplierModel,
)
from orm.product import ProductModel
from schemas import ApplicationResponse, Order, OrderHistory, OrderStatus
from schemas.uploads import PaginationUpload
from typing_ import RouteReturnT

router = APIRouter()


async def get_order(session: AsyncSession, order_id: int, seller_id: int) -> OrderModel:
    order = (
        (
            await session.execute(
                select(OrderModel)
                .where(
                    OrderModel.id == order_id,
                    OrderModel.seller_id == seller_id,
                    OrderModel.is_cart.is_(True),
                )
                .options(selectinload(OrderModel.details))
            )
        )
        .scalars()
        .unique()
        .one_or_none()
    )
    if not order:
        raise exceptions.BadRequestException(detail="Specified invalid order id")
    return order


async def compare_bundle_lists(
    order_variation_pod_ids: List[BundleVariationPodAmountModel],
    input_variation_pod_ids: List[int],
) -> Optional[Dict[int, int]]:
    if not input_variation_pod_ids:
        return None
    order_pod_ids = {item.bundle_variation_pod_id: item.id for item in order_variation_pod_ids}
    for bundle_variation_pod_id in input_variation_pod_ids:
        try:
            order_pod_ids.pop(bundle_variation_pod_id)
        except KeyError:
            raise exceptions.BadRequestException(
                detail=f"Specified invalid bundle variation pod id: {bundle_variation_pod_id}"
            )
    return order_pod_ids


async def create_new_order(session: AsyncSession, seller_id: int) -> OrderModel:
    order = (
        (
            await session.execute(
                insert(OrderModel).values(seller_id=seller_id, is_cart=True).returning(OrderModel)
            )
        )
        .scalars()
        .unique()
        .one_or_none()
    )
    if not order:
        raise exceptions.BadRequestException(detail="Error on new order create")
    return order


async def create_order_core(
    order_id: int,
    seller_id: int,
    bundle_variation_pod_ids: List[int],
    address_id: int,
    session: AsyncSession,
) -> None:
    order = await get_order(session=session, seller_id=seller_id, order_id=order_id)
    not_selected_variation_pod_ids = await compare_bundle_lists(
        order.details, bundle_variation_pod_ids
    )
    if not_selected_variation_pod_ids:
        new_order = await create_new_order(session=session, seller_id=seller_id)
        for variation_pod_id in not_selected_variation_pod_ids.keys():
            await session.execute(
                update(BundleVariationPodAmountModel)
                .where(
                    and_(
                        BundleVariationPodAmountModel.order_id == order.id,
                        BundleVariationPodAmountModel.bundle_variation_pod_id == variation_pod_id,
                    )
                )
                .values(order_id=new_order.id)
            )

    order.is_cart = False
    order.address_id = address_id

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
    description="Turn cart into order (after successful payment)\
    \nEmpty bundle_variation_pod_ids == all variations in order selected",
    summary="WORKS: create order from a cart.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def create_order(
    user: SellerAuthorization,
    session: DatabaseSession,
    bundle_variation_pod_ids: List[int],
    address_id: int = Body(),
    order_id: int = Path(...),
) -> RouteReturnT:
    await create_order_core(
        order_id=order_id,
        seller_id=user.seller.id,
        session=session,
        bundle_variation_pod_ids=bundle_variation_pod_ids,
        address_id=address_id,
    )

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
                selectinload(BundleVariationPodModel.product).selectinload(ProductModel.images),
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


async def get_orders_by_ids_core(
    session: AsyncSession, ids: List[int], user: SellerAuthorization
) -> List[OrderModel]:
    query = (
        select(OrderModel)
        .where(
            OrderModel.seller_id == user.seller.id,
            OrderModel.is_cart.is_(True),
            OrderModel.id.in_(ids),
        )
        .options(
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .options(
                selectinload(BundleVariationPodModel.prices),
                selectinload(BundleVariationPodModel.product).options(
                    selectinload(ProductModel.images),
                    selectinload(ProductModel.supplier).selectinload(SupplierModel.company),
                ),
            ),
        )
    )

    return (await session.execute(query)).scalars().all()


@router.post(
    path="/",
    summary="Get orders by ids for checkout page",
    response_model=ApplicationResponse[List[Order]],
    status_code=status.HTTP_200_OK,
)
async def get_orders_by_ids(
    ids: List[int],
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    orders = await get_orders_by_ids_core(session=session, ids=ids, user=user)
    return {"ok": True, "result": orders}
