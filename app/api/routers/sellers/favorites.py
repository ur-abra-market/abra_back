from corecrud import Limit, Offset, Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from orm import BundleVariationPodModel, ProductModel, SellerFavoriteModel, SellerModel
from schemas import ApplicationResponse, Seller
from schemas.uploads import PaginationUpload, ProductIdUpload
from typing_ import RouteReturnT

router = APIRouter()


async def add_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    seller_favorite = await crud.sellers_favorites.select.one(
        Where(
            and_(
                SellerFavoriteModel.seller_id == seller_id,
                SellerFavoriteModel.product_id == product_id,
            ),
        ),
        session=session,
    )
    if seller_favorite:
        raise exceptions.AlreadyExistException(detail="Product is already add to favorite")

    await crud.sellers_favorites.insert.one(
        Values(
            {
                SellerFavoriteModel.seller_id: seller_id,
                SellerFavoriteModel.product_id: product_id,
            }
        ),
        Returning(SellerFavoriteModel.id),
        session=session,
    )


@router.post(
    path="/add",
    summary="WORKS: add product in favorite",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def add_favorite(
    user: SellerAuthorization,
    session: DatabaseSession,
    data: ProductIdUpload = Body(...),
) -> RouteReturnT:
    await add_favorite_core(seller_id=user.seller.id, product_id=data.product_id, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def remove_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    await crud.sellers_favorites.delete.one(
        Where(
            and_(
                SellerFavoriteModel.seller_id == seller_id,
                SellerFavoriteModel.product_id == product_id,
            ),
        ),
        Returning(SellerFavoriteModel.id),
        session=session,
    )


@router.delete(
    path="/remove",
    summary="WORKS: remove product in favorite",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def remove_favorite(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
) -> RouteReturnT:
    await remove_favorite_core(seller_id=user.seller.id, product_id=product_id, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def show_favorites_core(
    session: AsyncSession,
    seller_id: int,
    offset: int,
    limit: int,
) -> SellerModel:
    return await crud.sellers.select.one(
        Where(SellerModel.id == seller_id),
        Options(
            selectinload(SellerModel.favorites),
            selectinload(SellerModel.favorites).selectinload(ProductModel.category),
            selectinload(SellerModel.favorites).selectinload(ProductModel.tags),
            selectinload(SellerModel.favorites)
            .selectinload(ProductModel.bundle_variation_pods)
            .selectinload(BundleVariationPodModel.prices),
        ),
        Offset(offset),
        Limit(limit),
        session=session,
    )


@router.get(
    path="/",
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[Seller],
    status_code=status.HTTP_200_OK,
)
async def show_favorites(
    user: SellerAuthorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_favorites_core(
            session=session,
            seller_id=user.seller.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }
