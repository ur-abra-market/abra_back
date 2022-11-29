import hashlib
import imghdr
import logging
import os
import boto3
from app.classes.response_models import *
from app.database import get_session
from app.database.models import *
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from app.logic import utils
from app.logic.consts import *
from sqlalchemy import and_, delete, insert, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
import json


sellers = APIRouter()


sellers.get("/sellers/get_seller_info/")
async def get_seller_info(
    # Authorize: AuthJWT = Depends(),
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Authorize.jwt_required()
    # user_email = json.loads(Authorize.get_jwt_subject())["email"]
    # user_id = await User.get_user_id(email=user_email)

    result = dict()


    user_query = await session.execute(
        select(
            User.first_name,
            User.last_name,
            User.email,
            User.phone
        )\
        .where(User.id.__eq__(user_id))
    )
    user_query = user_query.fetchone()

    # should we query for password? ofc no, mb

    notifications_query = await session.execute(
        select(
            UserNotification.on_discount,
            UserNotification.on_order_updates,
            UserNotification.on_order_reminders,
            UserNotification.on_stock_again,
            UserNotification.on_product_is_cheaper,
            UserNotification.on_your_favorites_new,
            UserNotification.on_account_support
        )\
        .where(UserNotification.user_id.__eq__(user_id))
    )
    notifications_query = notifications_query.fetchone()

    # profile_info = await session.execute(
    #     select(User.first_name, User.last_name, )
    # )