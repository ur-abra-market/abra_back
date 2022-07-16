from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT


login = APIRouter()


@login.post("/", summary='WORKS: User login (with token creating).')
           # response_model=LoginOut, responses={404: {"model": LoginError}})
async def login_user(user_data: LoginIn, Authorize: AuthJWT = Depends()):
    access_token = Authorize.create_access_token(subject=user_data.username)
    refresh_token = Authorize.create_refresh_token(subject=user_data.username)
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    result = await c.login_user(user_data=user_data)
    if result.status_code == 200:
        return {"msg": "Successfully login"}
    else:
        return {"msg": "Nope"}


@login.delete('/logout', summary='WORKS: User logout (token deleting).')
async def logout_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return {"msg": "Successfully logout"}


@login.post("/password/", summary='WORKS: Change password.')
async def change_password(user_data: ChangePasswordIn,
                          Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    result = await c.change_password(user_data=user_data,
                                     user_email=user_email)
    return result


@login.post("/forgot-password/")
async def forgot_password(email: MyEmail):
    result = await c.reset_password(email.email)
    return result