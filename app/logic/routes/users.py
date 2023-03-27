import os
import json
import logging
from pydantic import BaseModel
from app.settings import AWS_S3_IMAGE_USER_LOGO_BUCKET
from app.logic.consts import *
from app.logic.queries import *
from app.logic import utils
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.database.models import *


class GetRoleOut(BaseModel):
    is_supplier: bool


class SearchesOut(BaseModel):
    search_query: str
    datetime: str


class PhoneNumber(BaseModel):
    number: str


class UpdateUserNotification(BaseModel):
    on_discount: bool = False
    on_order_updates: bool = False
    on_order_reminders: bool = False
    on_stock_again: bool = False
    on_product_is_cheaper: bool = False
    on_your_favorites_new: bool = False
    on_account_support: bool = False


users = APIRouter()


@users.get("/get_role/", summary="WORKS: Get user role.", response_model=GetRoleOut)
async def get_user_role(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())["email"]
    if user_email:
        is_supplier = await User.get_user_role(email=user_email)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"is_supplier": is_supplier}
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_SEARCHES")


@users.get(
    "/latest_searches/",
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=SearchesOut,
)
async def get_latest_searches_for_user(
    Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)
    searches = await session.execute(
        select(UserSearch.search_query, UserSearch.datetime).where(
            UserSearch.user_id.__eq__(user_id)
        )
    )
    searches = [
        dict(search_query=row[0], datetime=str(row[1])) for row in searches if searches
    ]

    if searches:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": searches}
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_SEARCHES")


@users.post(
    "/upload_logo_image/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
)
async def upload_logo_image(
    file: UploadFile,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)

    _, file_extension = os.path.splitext(file.filename)

    contents = await file.read()
    await file.seek(0)

    # file validation
    if not utils.is_image(contents=contents):
        logging.error("File is not an image: '%s'", file.filename)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_IMAGE")

    new_file_url = await utils.upload_file_to_s3(
        bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET,
        file=utils.Dict(file=file.file, extension=file_extension),
        contents=contents,
    )

    # get user logo
    user_logo = await session.execute(
        select(UserImage).where(UserImage.user_id == user_id)
    )
    user_logo = user_logo.scalar()

    # if it's not the same image
    if not user_logo.source_url == new_file_url:
        # create thumbnale
        thumb_file = utils.thumbnail(
            contents=contents, content_type=file.content_type.split("/")[-1]
        )
        thumb_url = await utils.upload_file_to_s3(
            bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET,
            file=utils.Dict(file=thumb_file, extension=file_extension),
            contents=thumb_file.getvalue(),
        )
        thumb_file.close()

        # remove old files from s3
        if user_logo.source_url:
            files_to_remove = [
                utils.Dict(
                    bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET,
                    key=user_logo.source_url.split(".com/")[-1],
                ),
                utils.Dict(
                    bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET,
                    key=user_logo.thumbnail_url.split(".com/")[-1],
                ),
            ]
            await utils.remove_files_from_s3(files=files_to_remove)

        # update db with new image and thumbnail
        await session.execute(
            update(UserImage)
            .where(UserImage.user_id == user_id)
            .values(source_url=new_file_url, thumbnail_url=thumb_url)
        )

        logging.info(
            "User logo is updated for user_id '%s', image_url='%s'",
            user_id,
            new_file_url,
        )

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_UPDATED_SUCCESSFULLY"},
    )


@users.get("/get_notifications/", summary="WORKS: Displaying the notification switch")
async def get_notification_switch(
    Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(user_email)
    user_current_notification = await session.execute(
        select(
            UserNotification.on_discount,
            UserNotification.on_order_updates,
            UserNotification.on_order_reminders,
            UserNotification.on_stock_again,
            UserNotification,
            UserNotification.on_product_is_cheaper,
            UserNotification.on_your_favorites_new,
            UserNotification.on_account_support,
        ).where(UserNotification.user_id == user_id)
    )

    user_current_notification = user_current_notification.first()
    user_current_notification = dict(user_current_notification)
    del user_current_notification["UserNotification"]
    if user_current_notification:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=user_current_notification
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOTIFY_NOT_FOUND"
        )


@users.patch(
    "/update_notification/",
    summary="WORKS: Switch notification distribution",
)
async def update_notification(
    notification_params: UpdateUserNotification,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(user_email)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_EXISTS"
        )

    update_params = dict()
    for param, value in notification_params:
        if value is not None:
            update_params[param] = value

    await session.execute(
        update(UserNotification)
        .where(UserNotification.user_id == user_id)
        .values(update_params)
    )

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result:": "NOTIFICATION_UPDATED_SUCCESSFULLY"},
    )


@users.get("/show_favorites/", summary="WORKS: Shows all favorite products")
async def show_favorites(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)
    products_info = []

    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_SELLER"
        )

    favorite_products_ids = await session.execute(
        select(SellerFavorite.product_id).where(
            SellerFavorite.seller_id.__eq__(seller_id)
        )
    )
    product_ids = favorite_products_ids.fetchall()
    for product_id in product_ids:
        product_id = product_id[0]

        grade = await Product.get_product_grade(product_id=product_id)

        category_params = await session.execute(
            select(Category.id, Category.name)
            .join(Product)
            .where(Product.id.__eq__(product_id))
        )
        category_id, category_name = category_params.fetchone()
        category_path = await Category.get_category_path(category=category_name)

        product_name = await session.execute(
            select(Product.name).where(Product.id.__eq__(product_id))
        )
        product_name = product_name.scalar()

        tags = await Tags.get_tags_by_product_id(product_id=product_id)

        colors = await session.execute(
            text(QUERY_FOR_COLORS.format(product_id=product_id))
        )
        colors = [row[0] for row in colors if colors]

        sizes = await session.execute(
            text(QUERY_FOR_SIZES.format(product_id=product_id))
        )
        sizes = [row[0] for row in sizes if sizes]

        monthly_actual_demand = await session.execute(
            text(QUERY_FOR_MONTHLY_ACTUAL_DEMAND.format(product_id=product_id))
        )
        monthly_actual_demand = monthly_actual_demand.scalar()
        monthly_actual_demand = monthly_actual_demand if monthly_actual_demand else "0"

        daily_actual_demand = await session.execute(
            text(QUERY_FOR_DAILY_ACTUAL_DEMAND.format(product_id=product_id))
        )
        daily_actual_demand = daily_actual_demand.scalar()
        daily_actual_demand = daily_actual_demand if daily_actual_demand else "0"

        prices = await session.execute(text(QUERY_FOR_PRICES.format(product_id)))
        prices = [dict(row) for row in prices if prices]

        supplier_info = await Supplier.get_supplier_info(product_id=product_id)

        display_type = await PropertyDisplayType.get_display_name_by_property('size')

        product_info = dict(
            product_id=product_id,
            grade=grade,
            category_id=category_id,
            category_path=category_path,
            product_name=product_name,
            tags=tags,
            colors=colors,
            sizes=sizes,
            display_type=display_type,
            monthly_actual_demand=monthly_actual_demand,
            daily_actual_demand=daily_actual_demand,
            prices=prices,
            supplier_info=supplier_info,
        )
        products_info.append(product_info)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": products_info}
    )


@users.patch("/change_phone_number/", summary="WORKS: Allows user to change his phone number")
async def change_phone_number(
    phone: PhoneNumber,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(user_email)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_EXIST"
        )
    phone_number = {"phone": phone.number}
    await session.execute(
        update(User).where(User.id.__eq__(user_id)).values(phone_number)
    )
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "result:": "PHONE_NUMBER_WAS_UPDATED",
            "new_phone_number": phone.number,
        },
    )
