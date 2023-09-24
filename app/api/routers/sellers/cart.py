from typing import List

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from orm import (
    BundleModel,
    BundleVariationModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
)
from schemas import ApplicationResponse, Order
from typing_ import RouteReturnT

router = APIRouter()


async def add_to_cart_core(
    session: AsyncSession,
    seller_id: int,
    product_id: int,
    bundle_variation_pod_id: int,
    amount: int,
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
        .one_or_none()
    )

    if not order:
        # create an order if there's no one
        order = await crud.orders.insert.one(
            Values(
                {
                    OrderModel.seller_id: seller_id,
                    OrderModel.is_cart: True,
                }
            ),
            Returning(OrderModel),
            session=session,
        )
    elif list(
        filter(lambda x: x.bundle_variation_pod_id == bundle_variation_pod_id, order.details)
    ):
        # expand the bundle_variation_pod_amount if it exists
        await crud.bundles_variations_pods_amount.update.one(
            Where(
                BundleVariationPodAmountModel.bundle_variation_pod_id == bundle_variation_pod_id,
                BundleVariationPodAmountModel.order_id == order.id,
            ),
            Values(
                {
                    BundleVariationPodAmountModel.amount: order.details[0].amount + amount,
                }
            ),
            Returning(BundleVariationPodAmountModel),
            session=session,
        )
        return order

    # add bundle_variation_pod_amount to order if there's no one there
    await crud.bundles_variations_pods_amount.insert.one(
        Values(
            {
                BundleVariationPodAmountModel.bundle_variation_pod_id: bundle_variation_pod_id,
                BundleVariationPodAmountModel.order_id: order.id,
                BundleVariationPodAmountModel.amount: amount,
            }
        ),
        Returning(BundleVariationPodAmountModel),
        session=session,
    )

    await session.refresh(order)
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
    product_id: int = Query(),
    bundle_variation_pod_id: int = Query(),
    amount: int = Query(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_to_cart_core(
            session=session,
            seller_id=user.seller.id,
            product_id=product_id,
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
) -> List[OrderModel]:
    return await crud.orders.select.many(
        Where(
            OrderModel.seller_id == seller_id,
            OrderModel.is_cart.is_(True),
        ),
        Options(
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.product),
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.prices),
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.bundle_variations)
            .selectinload(BundleVariationModel.bundle)
            .selectinload(BundleModel.variation_values),
        ),
        session=session,
    )


@router.get(
    path="/",
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[Order]],
    status_code=status.HTTP_200_OK,
)
async def show_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_cart_core(
            session=session,
            seller_id=user.seller.id,
        ),
    }
