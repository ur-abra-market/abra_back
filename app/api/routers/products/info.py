from typing import List

from corecrud import Where
from fastapi import APIRouter
from fastapi.param_functions import Path
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import AuthorizationOptional, DatabaseSession
from orm import (
    BundlableVariationValueModel,
    BundleModel,
    BundleVariationPodModel,
    ProductImageModel,
    ProductModel,
    ProductReviewModel,
    PropertyValueModel,
    SellerFavoriteModel,
    SupplierModel,
    UserModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, ProductImage, ProductRating
from typing_ import RouteReturnT

router = APIRouter()


async def get_product_images_core(
    product_id: int,
    session: AsyncSession,
) -> List[ProductImageModel]:
    return await crud.products_images.select.many(
        Where(ProductImageModel.product_id == product_id),
        session=session,
    )


@router.get(
    path="/images",
    summary="WORKS: Get product images by product_id.",
    response_model=ApplicationResponse[List[ProductImage]],
    status_code=status.HTTP_200_OK,
)
async def get_product_images(
    session: DatabaseSession,
    product_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_images_core(product_id=product_id, session=session),
    }


async def get_info_for_product_card_core(
    session: AsyncSession,
    product_id: int,
    user: UserModel,
) -> ProductRating:
    query = (
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .options(selectinload(ProductModel.category))
        .options(selectinload(ProductModel.images))
        .options(
            selectinload(ProductModel.bundle_variation_pods).selectinload(
                BundleVariationPodModel.prices
            )
        )
        .options(selectinload(ProductModel.supplier).selectinload(SupplierModel.company))
        .options(selectinload(ProductModel.tags))
        .options(selectinload(ProductModel.properties).selectinload(PropertyValueModel.type))
        .options(
            selectinload(ProductModel.product_variations)
            .selectinload(VariationValueToProductModel.variation)
            .selectinload(VariationValueModel.type)
        )
        .options(selectinload(ProductModel.bundles).selectinload(BundleModel.variations))
        .options(selectinload(ProductModel.bundles).selectinload(BundleModel.variation_values))
        .options(selectinload(ProductModel.bundles).selectinload(BundleModel.prices))
        .options(
            selectinload(ProductModel.bundles)
            .selectinload(BundleModel.variation_values)
            .selectinload(BundlableVariationValueModel.product_variation)
            .selectinload(VariationValueToProductModel.variation)
            .selectinload(VariationValueModel.type)
        )
    )

    # subquery_bundle = (
    #     select(VariationTypeModel)
    #     .where(ProductModel.id == product_id)
    #     .join(VariationTypeModel.values)
    #     .join(VariationValueModel.product_variation)
    #     .join(VariationValueToProductModel.bundlable_product_variation_value)
    #     .join(BundlableVariationValueModel.bundle)
    # )

    if user and user.seller:
        subquery = select(SellerFavoriteModel.product_id).where(
            SellerFavoriteModel.seller_id == user.seller.id
        )
        query = query.outerjoin(ProductModel.favorites_by_users).options(
            with_expression(ProductModel.is_favorite, ProductModel.id.in_(subquery))
        )
    product = (await session.execute(query)).scalar_one_or_none()
    if not product:
        raise exceptions.NotFoundException(detail="Product not found")

    rating_list = (
        await session.execute(
            select(ProductReviewModel.grade_overall, func.count())
            .where(ProductReviewModel.product_id == product_id)
            .group_by(ProductReviewModel.grade_overall)
        )
    ).fetchall()
    feedbacks = {key: value for key, value in rating_list}

    return {
        "product": product,
        "feedbacks": feedbacks,
    }


@router.get(
    path="/",
    summary="WORKS (example 1-100, 1): Get info for product card p1.",
    response_model=ApplicationResponse[ProductRating],
    status_code=status.HTTP_200_OK,
)
async def get_info_for_product_card(
    user: AuthorizationOptional,
    session: DatabaseSession,
    product_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_info_for_product_card_core(
            session=session, product_id=product_id, user=user
        ),
    }
