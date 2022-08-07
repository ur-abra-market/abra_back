from fastapi import APIRouter, Depends, HTTPException, status
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT
from logic import pwd_hashing
from database.models import *
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update


password = APIRouter()


@password.post("/change/", 
               summary='WORKS (need csrf_access_token in headers): '
                       'Change password (token is needed).',
               response_model=ResultOut,
               responses={404: {"model": ResultOut}})
async def change_password(user_data: ChangePasswordIn,
                          Authorize: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user_id = await User.get_user_id(user_email)

    hashed_password_db = await session\
                    .execute(select(UserCreds.password)\
                    .where(UserCreds.user_id.__eq__(user_id)))
    hashed_password_db = hashed_password_db.scalar()
    is_passwords_match = \
        pwd_hashing.check_hashed_password(password=user_data.old_password,
                                          hashed=hashed_password_db)
    if hashed_password_db and is_passwords_match:
        hashed_password_new = \
            pwd_hashing.hash_password(password=user_data.new_password)
        await session.execute(update(UserCreds)\
                .where(UserCreds.user_id.__eq__(user_id))\
                .values(password=hashed_password_new))
        await session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "PASSWORD_CHANGED"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="INVALID_PASSWORD"
        )


@password.post("/forgot-password/",
               summary='WORKS: Send letter with link (token) to user email. Next step is /sheck-for token.',
               response_model=ResultOut)
async def forgot_password(email: MyEmail):
    result = await c.send_reset_message(email.email)
    return result


@password.post("/check-for-token/",
               summary="WORKS: Receive and check token. Next step is /reset-password.",
               response_model=ResultOut)
async def check_for_token(token: str):
    result = await c.check_token(token)
    return result


@password.patch("/reset-password/",
                summary='WORKS: reset and change password.',
                response_model=ResultOut)
async def reset_password(user_data: ResetPassword):
    result = await c.reset_user_password(user_email=user_data.email,
                                user_new_password=user_data.new_password,
                                user_confirm_new_password=user_data.confirm_password)
    return result
