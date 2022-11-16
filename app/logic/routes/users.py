import os
import json
import logging
from app.classes.response_models import *
from app.logic.consts import *
from app.logic import utils
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from sqlalchemy import and_, insert, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.database.models import *


users = APIRouter()


@users.get("/get_role",
           summary="get user role",
           response_model=GetRoleOut)
async def get_user_role(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())['email']
    if user_email:
        is_supplier = await User.get_user_role(email=user_email)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"is_supplier": is_supplier}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_SEARCHES"
        )


@users.get("/latest_searches/",
           summary='WORKS (example 5): Get latest searches by user_id.',
           response_model=SearchesOut)
async def get_latest_searches_for_user(user_id: int,
                                       session: AsyncSession = Depends(get_session)):
    searches = await session.\
        execute(select(UserSearch.search_query, UserSearch.datetime).
                where(UserSearch.user_id.__eq__(user_id)))
    searches = [dict(search_query=row[0], datetime=str(row[1]))
                for row in searches if searches]

    if searches:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": searches}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_SEARCHES"
        )


@users.post(
    "/upload_logo_image/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
)
async def upload_file_to_s3(
    file: UploadFile,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())['email']
    user_id = await User.get_user_id(email=user_email)

    _, file_extension = os.path.splitext(file.filename)

    contents = await file.read()
    await file.seek(0)

    # file validation
    if not utils.is_image(contents=contents):
        logging.error("File is not an image: '%s'", file.filename)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_IMAGE")

    url = await utils.upload_file_to_s3(
        bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET,
        file=utils.Dict(
            file=file.file,
            extension=file_extension
        ),
        contents=contents
    )

    # Upload data to DB
    existing_row = await session.execute(
        select(UserImage.id).where(
            UserImage.user_id == user_id,
            UserImage.source_url == url
        )
    )
    existing_row = existing_row.scalar()

    if not existing_row:
        thumb_file = utils.thumbnail(
            contents=contents,
            extension=file_extension
        )
        thumb_url = await utils.upload_file_to_s3(
            bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET,
            file=utils.Dict(
                file=thumb_file,
                extension=file_extension
            ),
            contents=thumb_file.getvalue()
        )
        thumb_file.close()

        await session.execute(
            update(UserImage).
            where(UserImage.user_id == user_id).
            values(
                source_url=url,
                thumbnail_url=thumb_url
            )
        )

        logging.info(
            "User logo is updated for user_id '%s', image_url='%s'",
            user_id,
            url,
        )

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_UPDATED_SUCCESSFULLY"},
    )
