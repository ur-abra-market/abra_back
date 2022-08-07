from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from classes.response_models import *
from database import get_session
from database.models import *
from logic import pwd_hashing


login = APIRouter()


@login.post("/", 
            summary='WORKS: User login (token creation).',
            response_model=ResultOut, responses={404: {"model": ResultOut}})
async def login_user(user_data: LoginIn,
                     Authorize: AuthJWT = Depends(),
                     session: AsyncSession = Depends(get_session)):
    user_id = await User.get_user_id(user_data.email)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WRONG_CREDENTIALS"
        )

    hashed_password_from_db = await session\
        .execute(select(UserCreds.password)\
        .where(UserCreds.user_id.__eq__(user_id)))
    hashed_password_from_db = hashed_password_from_db.scalar()

    is_passwords_match = \
        pwd_hashing.check_hashed_password(password=user_data.password,
                                          hashed=hashed_password_from_db)
    if hashed_password_from_db and is_passwords_match:
        access_token = \
            Authorize.create_access_token(subject=user_data.email)
        refresh_token = \
            Authorize.create_refresh_token(subject=user_data.email)
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "LOGIN_SUCCESSFUL"}
        )
        Authorize.set_access_cookies(encoded_access_token=access_token,
                                     response=response,
                                     max_age=ACCESS_TOKEN_EXPIRATION_TIME)
        Authorize.set_refresh_cookies(encoded_refresh_token=refresh_token,
                                      response=response,
                                      max_age=REFRESH_TOKEN_EXPIRATION_TIME)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WRONG_CREDENTIALS"
        )


@login.post("/refresh",
            summary='WORKS (need csrf_refresh_token in headers): '
                    'Refresh all tokens.',
            response_model=ResultOut)
def refresh_JWT_tokens(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    subject = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=subject)
    new_refresh_token = Authorize.create_refresh_token(subject=subject)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "TOKENS_REFRESHED"}
    )
    Authorize.set_access_cookies(encoded_access_token=new_access_token,
                                 response=response,
                                 max_age=ACCESS_TOKEN_EXPIRATION_TIME)
    Authorize.set_refresh_cookies(encoded_refresh_token=new_refresh_token,
                                  response=response,
                                  max_age=REFRESH_TOKEN_EXPIRATION_TIME)
    return response
