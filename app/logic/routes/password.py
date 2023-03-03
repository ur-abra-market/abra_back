from fastapi import APIRouter, Depends, HTTPException, status
from app.classes.response_models import ResultOut
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from app.logic import pwd_hashing
from app.database.models import *
from fastapi.responses import JSONResponse
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete
import uuid
from ..consts import BODY
from app.logic import utils
from os import getenv
import json
import re


class MyEmail(BaseModel):
    email: str


class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str


class ResetPassword(BaseModel):
    new_password: str
    confirm_password: str


password = APIRouter()


@password.post(
    "/change/",
    summary="WORKS (need X-CSRF-TOKEN in headers): "
    "Change password (token is needed).",
    response_model=ResultOut,
    responses={404: {"model": ResultOut}},
)
async def change_password(
    user_data: ChangePasswordIn,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    if user_data.old_password == user_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="SAME_PASSWORDS"
        )

    password_pattern = r"(?=.*[0-9])(?=.*[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}"
    if not re.fullmatch(password_pattern, user_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="PASSWORD_VALIDATION_ERROR",
        )

    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(user_email)

    hashed_password_db = await session.execute(
        select(UserCreds.password).where(UserCreds.user_id.__eq__(user_id))
    )
    hashed_password_db = hashed_password_db.scalar()
    is_passwords_match = pwd_hashing.check_hashed_password(
        password=user_data.old_password, hashed=hashed_password_db
    )
    if hashed_password_db and is_passwords_match:
        hashed_password_new = pwd_hashing.hash_password(password=user_data.new_password)
        await session.execute(
            update(UserCreds)
            .where(UserCreds.user_id.__eq__(user_id))
            .values(password=hashed_password_new)
        )
        await session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": "PASSWORD_CHANGED"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="INVALID_PASSWORD"
        )


@password.post(
    "/forgot_password/",
    summary="WORKS: Send letter with link (token) to user email. "
    "Next step is /check-for-token.",
    response_model=ResultOut,
)
async def forgot_password(email: MyEmail, session: AsyncSession = Depends(get_session)):
    existing_email = await session.execute(
        select(User.email).where(User.email.__eq__(email.email))
    )
    existing_email = existing_email.scalar()
    if not existing_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND"
        )
    reset_code = str(uuid.uuid1())
    user_id = await User.get_user_id(email.email)
    user_info = ResetToken(
        user_id=user_id, email=email.email, reset_code=reset_code, status=True
    )
    session.add(user_info)
    await session.commit()
    subject = "Сброс пароля"
    recipient = [email.email]
    body = BODY.format(user=email.email, host=getenv("APP_URL"), reset_code=reset_code)
    result = await utils.send_email(subject, recipient, body)
    return result


@password.post(
    "/check_for_token/",
    summary="WORKS: Receive and check token. Next step is /reset-password.",
    response_model=ResultOut,
)
async def check_for_token(token: str, session: AsyncSession = Depends(get_session)):
    existing_token = await session.execute(
        select(ResetToken.reset_code).where(ResetToken.reset_code == token)
    )
    for item in existing_token:
        if "".join(item) == token:
            return JSONResponse(status_code=200, content={"result": "TOKEN_IS_ACTIVE"})
        else:
            raise HTTPException(status_code=404, detail="RESET_TOKEN_HAS_EXPIRED")


@password.patch(
    "/reset_password/",
    summary="WORKS: reset and change password.",
    response_model=ResultOut,
)
async def reset_password(
        user_data: ResetPassword,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_optional()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]

    if user_data.new_password != user_data.confirm_password:
        raise HTTPException(status_code=404, detail="NEW_PASSWORD_IS_NOT_MATCHING")

    password_pattern = r"(?=.*[0-9])(?=.*[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}"
    if not re.fullmatch(password_pattern, user_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="PASSWORD_VALIDATION_ERROR",
        )

    user_id = await User.get_user_id(user_email)
    hashed_password = pwd_hashing.hash_password(user_data.new_password)
    await session.execute(
        update(UserCreds)
        .where(UserCreds.user_id.__eq__(user_id))
        .values(password=hashed_password)
    )
    await session.execute(delete(ResetToken).where(ResetToken.email == user_email))
    await session.commit()
    return JSONResponse(
        status_code=200,
        content={"result": "PASSWORD_HAS_BEEN_CHANGED_SUCCESSFULLY"}
    )
