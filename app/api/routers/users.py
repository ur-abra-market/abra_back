from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status
from fastapi.exceptions import HTTPException

from core.depends import auth_required, UserObjects, get_session
from core.tools import store
from orm import UserModel, UserSearchModel, UserNotificationModel, ProductModel, SellerFavoriteModel
from schemas import (
    ApplicationResponse,
    User,
    QueryPaginationRequest,
    UserNotification,
    BodyUserNotificationRequest,
    Product,
    UserSearch,
    BodyPhoneNumberRequest,
)

router = APIRouter()


@router.get(
    path="/getRole",
    description="Moved to /users/getUser",
    deprecated=True,
    summary="WORKS: Get user role.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
@router.get(
    path="/get_role",
    description="Moved to /users/getUser",
    deprecated=True,
    summary="WORKS: Get user role.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_user_role(
    user: UserObjects = Depends(auth_required),
) -> ApplicationResponse[User]:
    return {"ok": True, "result": user.schema, "detail": "This endpoint moved to `getUser`"}


@router.get(
    path="/latestSearches",
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=ApplicationResponse[List[UserSearch]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/latest_searches",
    description="Moved to /users/latestSearches",
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=ApplicationResponse[List[UserSearch]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_latest_searches(
    pagination: QueryPaginationRequest = Depends(),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[UserSearch]]:
    searches = await store.orm.users_searches.get_many(
        session=session,
        where=[UserSearchModel.id == user.schema.id],
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return {"ok": True, "result": searches}


@router.get(
    path="/getNotifications",
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[UserNotification],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_notifications",
    description="Moved to /users/getNotifications",
    deprecated=True,
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[UserNotification],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_notifications(
    user: UserObjects = Depends(auth_required), session: AsyncSession = Depends(get_session)
) -> ApplicationResponse[UserNotification]:
    return {
        "ok": True,
        "result": await store.orm.users_notifications.get_one(
            session=session,
            where=[UserNotificationModel.user_id == user.schema.id],
        ),
    }


@router.patch(
    path="/updateNotifications",
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.patch(
    path="/update_notification",
    description="Moved to /users/updateNotifications",
    deprecated=True,
    summary="WORKS: Displaying the notification switch",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def update_notifications(
    request: BodyUserNotificationRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await store.orm.users_notifications.update_one(
        session=session,
        values=request.dict(),
        where=UserNotificationModel.id == user.schema.id,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/showFavorites",
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/show_favorites",
    description="Moved to /users/showFavorites",
    deprecated=True,
    summary="WORKS: Shows all favorite products",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def show_favorites(
    pagination: QueryPaginationRequest = Depends(),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Product]]:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    return {
        "ok": True,
        "result": await store.orm.products.get_many(
            session=session,
            where=[SellerFavoriteModel.seller_id == user.schema.seller.id],
            options=[
                joinedload(ProductModel.category),
                joinedload(ProductModel.tags),
            ],
            offset=pagination.offset,
            limit=pagination.limit,
        ),
        "detail": "Not worked yet",
    }


@router.patch(
    path="/changePhoneNumber",
    summary="WORKS: Allows user to change his phone number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
@router.patch(
    path="/change_phone_number",
    description="Moved to /users/changePhoneNumber",
    deprecated=True,
    summary="WORKS: Allows user to change his phone number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def change_phone_number(
    request: BodyPhoneNumberRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await store.orm.users.update_one(
        session=session,
        values={
            UserModel.phone: request.number,
        },
        where=[UserModel.id == user.schema.id],
    )

    return {
        "ok": True,
        "result": True,
        "detail": {
            "new_phone_number": request.number,
        },
    }
