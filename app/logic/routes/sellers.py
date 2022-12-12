from app.database import get_session
from app.database.models import *
from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from app.logic.consts import *
from app.logic.queries import *
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


sellers = APIRouter()


@sellers.get("/sellers/get_seller_info/", summary="Not ready")
async def get_seller_info(
    # Authorize: AuthJWT = Depends(),
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    # Authorize.jwt_required()
    # user_email = json.loads(Authorize.get_jwt_subject())["email"]
    # user_id = await User.get_user_id(email=user_email)

    user_query = await session.execute(
        select(User.first_name, User.last_name, User.email, User.phone).where(
            User.id.__eq__(user_id)
        )
    )
    user_query = user_query.fetchone()

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


@sellers.post("/send_seller_info/", summary="")
async def send_seller_data_info(
    Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    pass
