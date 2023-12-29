from typing import List

from corecrud import Where
from fastapi import APIRouter
from fastapi.param_functions import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import AuthorizationOptional, DatabaseSession
from orm import (
    BundleModel,
    BundleVariationPodModel,
    ProductImageModel,
    ProductModel,
    PropertyValueModel,
    SellerFavoriteModel,
    SupplierModel,
    UserModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, Product, ProductImage
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
) -> ProductModel:
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
        .options(selectinload(ProductModel.supplier).selectinload(SupplierModel.user))
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
            selectinload(ProductModel.product_variations)
            .selectinload(VariationValueToProductModel.variation)
            .selectinload(VariationValueModel.product_variation)
        )
    )

    if user and user.seller:
        subquery = select(SellerFavoriteModel.product_id).where(
            SellerFavoriteModel.seller_id == user.seller.id
        )
        query = query.outerjoin(ProductModel.favorites_by_users).options(
            with_expression(ProductModel.is_favorite, ProductModel.id.in_(subquery))
        )
    product = (await session.execute(query)).scalars().one_or_none()
    if not product:
        raise exceptions.NotFoundException(detail="Product not found")

    return product


@router.get(
    path="/",
    summary="WORKS (example 1-100, 1): Get info for product card p1.",
    response_model=ApplicationResponse[Product],
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
