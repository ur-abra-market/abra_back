from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Query
from sqlalchemy import and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core import exceptions
from core.depends import DatabaseSession, SellerAuthorization
from orm import BundleVariationPodModel, ProductModel, SellerFavoriteModel
from schemas import ApplicationResponse, Product
from schemas.uploads import PaginationUpload, ProductIdUpload
from typing_ import RouteReturnT

router = APIRouter()


async def add_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    query_select = select(SellerFavoriteModel).where(
        and_(
            SellerFavoriteModel.seller_id == seller_id,
            SellerFavoriteModel.product_id == product_id,
        )
    )
    seller_favorite = (await session.execute(query_select)).scalar()
    if seller_favorite:
        raise exceptions.AlreadyExistException(detail="Product is already in favorites")
    query_insert = (
        insert(SellerFavoriteModel).values(seller_id=seller_id).values(product_id=product_id)
    )
    await session.execute(query_insert)
    await session.commit()


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
    query = delete(SellerFavoriteModel).where(
        and_(
            SellerFavoriteModel.seller_id == seller_id,
            SellerFavoriteModel.product_id == product_id,
        )
    )
    await session.execute(query)
    await session.commit()


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
) -> List[ProductModel]:
    product_list = select(SellerFavoriteModel.product_id).where(
        SellerFavoriteModel.seller_id == seller_id
    )
    return (
        (
            await session.execute(
                select(ProductModel)
                .where(ProductModel.id.in_(product_list))
                .options(selectinload(ProductModel.category))
                .options(selectinload(ProductModel.tags))
                .options(
                    selectinload(ProductModel.bundle_variation_pods).selectinload(
                        BundleVariationPodModel.prices
                    )
                )
                .offset(offset)
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )


@router.get(
    path="/",
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[List[Product]],
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
