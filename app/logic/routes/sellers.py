from app.database import get_session
from app.database.models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from app.logic.consts import *
from app.logic.queries import *
from sqlalchemy import select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import json


class SellerUserData(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]


class SellerUserNotification(BaseModel):
    on_discount: bool
    on_order_updates: bool
    on_order_reminders: bool
    on_stock_again: bool
    on_product_is_cheaper: bool
    on_your_favorites_new: bool
    on_account_support: bool


class SellerUserAddress(BaseModel):
    country: str = None
    area: str = None
    city: str = None
    street: str = None
    building: str = None
    appartment: str = None
    postal_code: str = None


class OrdersList(BaseModel):
    unpaid: Optional[int]
    to_be_shipped: Optional[int]
    shipped: Optional[int]
    to_be_reviewed: Optional[int]
    completed: Optional[int]


sellers = APIRouter()


@sellers.get(
    "/get_seller_info/",
    summary="WORKS: returns dict with profile info," \
            "adresses, notifications, photo information"
)
async def get_seller_info(
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)

    user_query = await session.execute(
        select(User.first_name, User.last_name, User.email, User.phone).where(
            User.id.__eq__(user_id)
        )
    )
    user_query = user_query.fetchone()
    user_profile_info = dict(user_query) \
        if user_query else {}

    notifications_query = await session.execute(
        select(
            UserNotification.on_discount,
            UserNotification.on_order_updates,
            UserNotification.on_order_reminders,
            UserNotification.on_stock_again,
            UserNotification.on_product_is_cheaper,
            UserNotification.on_your_favorites_new,
            UserNotification.on_account_support,
        ).where(UserNotification.user_id.__eq__(user_id))
    )
    notifications_query = notifications_query.fetchone()
    notification = dict(notifications_query)

    user_adresses_query = await session.execute(
        select(
            UserAdress.street,
            UserAdress.building,
            UserAdress.appartment,
            UserAdress.city,
            UserAdress.area,
            UserAdress.country,
            UserAdress.postal_code,
        ).where(UserAdress.user_id.__eq__(user_id))
    )
    user_adresses_query = user_adresses_query.fetchall()
    user_adresses = dict(user_adresses_query) \
        if user_adresses_query else {}

    profile_image_query = await session.execute(
        select(UserImage.thumbnail_url, UserImage.source_url) \
            .where(UserImage.user_id.__eq__(user_id))
    )
    profile_image_query = profile_image_query.fetchall()
    profile_image = dict(profile_image_query) \
        if profile_image_query else {}

    result = dict(
        user_profile_info=user_profile_info,
        user_adresses=user_adresses,
        notifications=notification,
        profile_image=profile_image
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": result}
    )


@sellers.get(
    "/get_order_status/",
    summary="Not working yet"
)
async def get_order_status(
        status: Optional[int] = None,
        # Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    # Authorize.jwt_required()
    # user_id = await User.get_user_id(email=user_email)

    # if isinstance(status, int):
    #     result = await session.execute(
    #         select()
    #     )
    pass


@sellers.post(
    "/send_seller_info/",
    summary="WORKS: update seller data, full adress is required, notifications - 1 route for all norificatios"
)
async def send_seller_data_info(
        seller_data: SellerUserData = None,
        seller_address_data: SellerUserAddress = None,
        seller_notifications_data: SellerUserNotification = None,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)

    user_data: Optional[dict] = \
        {key: value for key, value in dict(seller_data).items() if value} \
            if seller_data else None
    address_data: Optional[dict] = \
        {key: value for key, value in dict(seller_address_data).items() if value} \
            if seller_address_data else None
    notifications_data: Optional[dict] = \
        {key: value for key, value in dict(seller_notifications_data).items()} \
            if seller_notifications_data else None

    if user_data:
        await session.execute(
            update(User).where(User.id.__eq__(user_id)).values(**(user_data))
        )
    if address_data:
        await session.execute(
            update(UserAdress) \
                .where(UserAdress.user_id.__eq__(user_id)) \
                .values(**address_data)
        )
    if notifications_data:
        await session.execute(
            update(UserNotification) \
                .where(UserNotification.user_id.__eq__(user_id)) \
                .values(**notifications_data)
        )
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": "DATA_HAS_BEEN_SENT"}
    )


@sellers.post('/add_seller_address/')
async def add_seller_address(
        seller_address_data: SellerUserAddress,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)
    if seller_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='USER_NOT_SELLER'
        )

    is_address = (await session.execute(
        select(UserAdress)
        .where(UserAdress.user_id.__eq__(seller_id))
    )).first()

    if is_address:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail='ADDRESS_ALREADY_ADDED'
        )
    seller_address_data = dict(seller_address_data)
    seller_address_data['user_id'] = seller_id
    await session.execute(insert(UserAdress).values(seller_address_data))
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'result': 'ADDRESS_SUCCESSFULLY_ADDED'}
    )


@sellers.patch('/update_seller_address/', response_model=SellerUserAddress, response_model_exclude_unset=True)
async def change_seller_address(
        seller_address_data: SellerUserAddress,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)
    if seller_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='USER_NOT_SELLER'
        )
    seller_address_data = {key: value for key, value in dict(seller_address_data).items() if value is not None}
    await session.execute(
        update(UserAdress)
        .values(dict(seller_address_data))
        .where(UserAdress.user_id.__eq__(seller_id))
    )
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'result': 'ADDRESS_WAS_UPDATED'}
    )


@sellers.get('/get_seller_address/', response_model=SellerUserAddress)
async def get_seller_address(
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)
    if seller_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='USER_NOT_SELLER'
        )

    seller_address = (await session.execute(
        select(UserAdress.country,
               UserAdress.area,
               UserAdress.city,
               UserAdress.street,
               UserAdress.building,
               UserAdress.appartment,
               UserAdress.postal_code)
        .where(UserAdress.user_id.__eq__(seller_id))
    )).first()
    seller_address = jsonable_encoder(seller_address)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'result': seller_address}
    )


@sellers.delete('/remove_seller_address/')
async def remove_seller_address(
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)
    if seller_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='USER_NOT_SELLER'
        )

    await session.execute(delete(UserAdress).where(UserAdress.user_id.__eq__(seller_id)))
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'result': 'ADDRESS_WAS_DELETED'}
    )