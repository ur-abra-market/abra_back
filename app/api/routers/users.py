from typing import Any, List

from corecrud import (
    GroupBy,
    Join,
    Limit,
    Offset,
    Options,
    OuterJoin,
    Returning,
    SelectFrom,
    Values,
    Where,
)
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Query
from fastapi.responses import Response
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette import status

from core.app import crud
from core.depends import AuthJWT, Authorization, DatabaseSession, SellerAuthorization
from orm import (
    BundleVariationPodModel,
    OrderModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    SellerFavoriteModel,
    SellerModel,
    UserModel,
    UserSearchModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, Seller, User, UserSearch
from schemas.uploads import ChangeEmailUpload, PaginationUpload, UserDataUpdateUpload
from typing_ import RouteReturnT
from utils.cookies import unset_jwt_cookies

router = APIRouter()


async def get_latest_searches_core(
    session: AsyncSession, user_id: int, offset: int, limit: int
) -> List[UserSearch]:
    return await crud.users_searches.select.many(
        Where(UserSearchModel.user_id == user_id),
        Offset(offset),
        Limit(limit),
        session=session,
    )


@router.get(
    path="/latestSearches",
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=ApplicationResponse[List[UserSearch]],
    status_code=status.HTTP_200_OK,
)
async def get_latest_searches(
    user: Authorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_latest_searches_core(
            session=session,
            user_id=user.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
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
    path="/showFavorites",
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


async def change_email_core(
    session: AsyncSession,
    user_id: int,
    email: str,
) -> None:
    await crud.users.update.one(
        Values(
            {
                UserModel.email: email,
            }
        ),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.post(
    path="/changeEmail",
    summary="WORKS: allows user to change his email",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_email(
    user: Authorization,
    session: DatabaseSession,
    request: ChangeEmailUpload = Body(...),
) -> RouteReturnT:
    await change_email_core(
        session=session,
        user_id=user.id,
        email=request.confirm_email,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/isFavorite",
    summary="WORKS: returns is product in favorites",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def is_product_favorite(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
) -> RouteReturnT:
    seller_favorite = await crud.sellers_favorites.select.one(
        Where(
            SellerFavoriteModel.seller_id == user.seller.id,
            SellerFavoriteModel.product_id == product_id,
        ),
        session=session,
    )

    return {
        "ok": True,
        "result": bool(seller_favorite),
    }


async def delete_account_core(session: AsyncSession, user_id: int) -> None:
    await crud.users.update.one(
        Values({UserModel.is_deleted: True}),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.delete(
    path="/account/delete",
    summary="WORKS: Delete user account.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_account(
    response: Response,
    authorize: AuthJWT,
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    await delete_account_core(session=session, user_id=user.id)
    unset_jwt_cookies(response=response, authorize=authorize)

    return {
        "ok": True,
        "result": True,
    }


async def get_personal_info_core(session: AsyncSession, user_id: int) -> UserModel:
    return await crud.users.select.one(
        Where(UserModel.id == user_id),
        Options(joinedload(UserModel.country)),
        session=session,
    )


@router.get(
    path="/account/personalInfo",
    summary="WORKS: get UserModel information such as: first_name, last_name, country_code, phone_number, country_data",
    response_model=ApplicationResponse[User],
    response_model_exclude={
        "result": {
            "admin",
            "seller",
            "supplier",
        },
    },
    status_code=status.HTTP_200_OK,
)
async def get_personal_info(user: Authorization, session: DatabaseSession) -> RouteReturnT:
    return {"ok": True, "result": await get_personal_info_core(session=session, user_id=user.id)}


async def update_account_info_core(
    session: AsyncSession,
    user_id: int,
    request: UserDataUpdateUpload,
) -> None:
    await crud.users.update.one(
        Values(request.dict()),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.post(
    path="/account/personalInfo/update",
    summary="WORKS: updated UserModel information such as: first_name, last_name, country_code, phone_number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_account_info(
    user: Authorization,
    session: DatabaseSession,
    request: UserDataUpdateUpload = Body(...),
) -> RouteReturnT:
    await update_account_info_core(session=session, user_id=user.id, request=request)

    return {
        "ok": True,
        "result": True,
    }


async def get_seller_orders_core(
    session: AsyncSession,
    seller_id: int,
) -> List[Any]:
    return await crud.raws.select.many(
        Where(
            OrderModel.seller_id == seller_id,
        ),
        Join(
            OrderStatusModel,
            OrderModel.status_id == OrderStatusModel.id,
        ),
        Join(
            OrderProductVariationModel,
            OrderModel.id == OrderProductVariationModel.order_id,
        ),
        Join(
            ProductVariationCountModel,
            ProductVariationCountModel.id == OrderProductVariationModel.product_variation_count_id,
        ),
        Join(
            VariationValueToProductModel,
            ProductVariationCountModel.product_variation_value1_id
            == VariationValueToProductModel.id,
        ),
        Join(ProductModel, ProductModel.id == VariationValueToProductModel.product_id),
        Join(ProductPriceModel, ProductPriceModel.product_id == ProductModel.id),
        OuterJoin(
            ProductImageModel,
            and_(
                ProductImageModel.product_id == VariationValueToProductModel.product_id,
            ),
        ),
        GroupBy(
            OrderModel.id,
            OrderModel.seller_id,
            ProductModel.id,
            ProductPriceModel.value,
            OrderStatusModel.name,
        ),
        nested_select=[
            OrderModel.id.label("order_id"),
            OrderModel.seller_id,
            ProductModel.id.label("product_id"),
            ProductPriceModel.value.label("price_value"),
            func.array_agg(ProductImageModel.image_url).label("product_image_urls"),
            OrderStatusModel.name.label("status_name"),
        ],
        session=session,
    )


@router.get(
    path="/orders",
    summary="WORKS: get list of orders of a particular user",
    response_model=ApplicationResponse[List[RouteReturnT]],
    status_code=status.HTTP_200_OK,
)
async def get_seller_orders(
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_seller_orders_core(
            session=session,
            seller_id=user.seller.id,
        ),
    }
