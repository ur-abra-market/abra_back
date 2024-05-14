from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends, Path, Query
from sqlalchemy import and_, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.depends import DatabaseSession, SellerAuthorization
from core.exceptions import NotFoundException
from orm import (
    BundleModel,
    BundleProductVariationValueModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
    SupplierModel,
)
from orm.bundlable_variation_value import BundlableVariationValueModel
from orm.product import ProductModel
from schemas import ApplicationResponse, Order
from schemas.uploads import PaginationUpload
from typing_ import RouteReturnT

router = APIRouter()


async def add_to_cart_core(
    session: AsyncSession,
    seller_id: int,
    bundle_variation_pod_id: int,
    amount: int,
) -> OrderModel:
    order = (
        (
            await session.execute(
                select(OrderModel)
                .options(selectinload(OrderModel.details))
                .join(OrderModel.details)
                .where(
                    and_(
                        OrderModel.seller_id == seller_id,
                        OrderModel.is_cart.is_(True),
                        BundleVariationPodAmountModel.bundle_variation_pod_id
                        == bundle_variation_pod_id,
                    )
                )
            )
        )
        .scalars()
        .unique()
        .one_or_none()
    )

    if order is None:
        order = (
            (
                await session.execute(
                    insert(OrderModel)
                    .values(seller_id=seller_id, is_cart=True)
                    .returning(OrderModel)
                )
            )
            .scalars()
            .unique()
            .one_or_none()
        )

    elif any(pod.bundle_variation_pod_id == bundle_variation_pod_id for pod in order.details):
        existing_pod = next(
            pod for pod in order.details if pod.bundle_variation_pod_id == bundle_variation_pod_id
        )
        existing_pod.amount += amount
        return order

    await session.execute(
        insert(BundleVariationPodAmountModel).values(
            order_id=order.id, bundle_variation_pod_id=bundle_variation_pod_id, amount=amount
        )
    )
    return order


@router.put(
    path="/addProduct",
    summary="WORKS: Add product to cart.",
    response_model=ApplicationResponse[Order],
    status_code=status.HTTP_200_OK,
)
async def add_to_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
    bundle_variation_pod_id: int = Query(),
    amount: int = Query(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_to_cart_core(
            session=session,
            seller_id=user.seller.id,
            bundle_variation_pod_id=bundle_variation_pod_id,
            amount=amount,
        ),
    }


async def remove_from_cart_core(
    session: AsyncSession,
    seller_id: int,
    product_id: int,
    bundle_variation_pod_id: int,
) -> OrderModel:
    order = (
        (
            await session.execute(
                select(OrderModel)
                .options(
                    selectinload(OrderModel.details).joinedload(
                        BundleVariationPodAmountModel.bundle_variation_pod
                    )
                )
                .join(OrderModel.details)
                .join(BundleVariationPodAmountModel.bundle_variation_pod)
                .where(
                    OrderModel.seller_id == seller_id,
                    OrderModel.is_cart.is_(True),
                    BundleVariationPodModel.product_id == product_id,
                )
            )
        )
        .scalars()
        .unique()
        .one()
    )

    bundle_variation_pod = list(
        filter(lambda x: x.bundle_variation_pod_id == bundle_variation_pod_id, order.details)
    )[0]

    await session.delete(bundle_variation_pod)

    if len(order.details) == 1:
        await session.delete(order)

    await session.refresh(order)
    return order


@router.delete(
    path="/removeProduct",
    summary="WORKS: Remove product from cart.",
    response_model=ApplicationResponse[Order],
    status_code=status.HTTP_200_OK,
)
async def remove_from_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(),
    bundle_variation_pod_id: int = Query(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await remove_from_cart_core(
            session=session,
            seller_id=user.seller.id,
            product_id=product_id,
            bundle_variation_pod_id=bundle_variation_pod_id,
        ),
    }


async def show_cart_core(
    session: AsyncSession,
    seller_id: int,
    offset: int,
    limit: int,
) -> List[OrderModel]:
    return (
        (
            await session.execute(
                select(OrderModel)
                .where(
                    OrderModel.seller_id == seller_id,
                    OrderModel.is_cart.is_(True),
                )
                .options(
                    selectinload(OrderModel.details)
                    .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
                    .selectinload(BundleVariationPodModel.product)
                    .selectinload(ProductModel.images)
                )
                .options(
                    selectinload(OrderModel.details)
                    .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
                    .selectinload(BundleVariationPodModel.product)
                    .selectinload(ProductModel.supplier)
                    .selectinload(SupplierModel.company)
                )
                .options(
                    selectinload(OrderModel.details)
                    .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
                    .selectinload(BundleVariationPodModel.prices)
                )
                .options(
                    selectinload(OrderModel.details)
                    .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
                    .selectinload(BundleVariationPodModel.bundle_variations)
                    .selectinload(BundleProductVariationValueModel.product_variation)
                )
                .options(
                    selectinload(OrderModel.details)
                    .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
                    .selectinload(BundleVariationPodModel.bundle_variations)
                    .selectinload(BundleProductVariationValueModel.bundle)
                    .selectinload(BundleModel.variation_values)
                    .selectinload(BundlableVariationValueModel.product_variation)
                )
                .offset(offset)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )


@router.get(
    path="",
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[Order]],
    status_code=status.HTTP_200_OK,
)
async def show_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_cart_core(
            session=session,
            seller_id=user.seller.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def set_amount_core(
    session: AsyncSession,
    bundle_variation_pod_id: int,
    seller_id: int,
    amount: int,
    product_id: int,
    order_id: int,
) -> OrderModel:
    query = (
        select(OrderModel)
        .join(BundleVariationPodAmountModel.bundle_variation_pod)
        .join(BundleVariationPodModel.product)
        .where(
            and_(
                OrderModel.id == order_id,
                OrderModel.seller_id == seller_id,
                ProductModel.id == product_id,
                BundleVariationPodAmountModel.bundle_variation_pod_id == bundle_variation_pod_id,
            )
        )
        .options(selectinload(OrderModel.details))
    )

    result = (await session.execute(query)).scalar_one_or_none()

    if result:
        if any(pod.bundle_variation_pod_id == bundle_variation_pod_id for pod in result.details):
            existing_pod = next(
                pod
                for pod in result.details
                if pod.bundle_variation_pod_id == bundle_variation_pod_id
            )
            existing_pod.amount = amount
        return result
    raise NotFoundException


@router.post(
    path="/orders/{order_id}/products/{product_id}/setAmount",
    summary="WORKS: Set amount of product in order.",
    response_model=ApplicationResponse[Order],
    status_code=status.HTTP_200_OK,
)
async def set_amount(
    user: SellerAuthorization,
    session: DatabaseSession,
    bundle_variation_pod_id: int = Query(),
    amount: int = Query(),
    product_id: int = Path(...),
    order_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await set_amount_core(
            session=session,
            seller_id=user.seller.id,
            bundle_variation_pod_id=bundle_variation_pod_id,
            amount=amount,
            product_id=product_id,
            order_id=order_id,
        ),
    }
