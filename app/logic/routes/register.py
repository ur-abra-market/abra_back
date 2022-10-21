from app.classes.response_models import *
from app.logic import utils
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.logic.consts import *
from app.database import get_session
from app.database.models import *
from app.logic import pwd_hashing
import logging
from os import getenv
from fastapi_jwt_auth import AuthJWT
import json


register = APIRouter()


@register.post("/email_confirmation_result/",
               summary='WORKS: Processing token that was sent to user '
                       'during the registration process.', 
               response_model=LoginOut)
async def receive_confirmation_result(token: ConfirmationToken,
                                Authorize: AuthJWT = Depends(),
                                session: AsyncSession = Depends(get_session)):
    try:
        decoded_token = utils.get_current_user(token.token)
        decoded_token = decoded_token.split("'")
        logging.info(decoded_token)
        existing_email = await session\
                        .execute(select(User.email)\
                        .where(User.email.__eq__(decoded_token[0])))
        existing_email = existing_email.scalar()
    # bad practice - catch just Exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_TOKEN"
        )

    if not existing_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_FOUND"
        )
    else:
        is_supplier = await session\
            .execute(select(User.is_supplier)\
            .where(User.email.__eq__(existing_email)))
        is_supplier = is_supplier.scalar()

        data_for_jwt = dict(email=existing_email,
                            is_supplier=int(is_supplier))
        data_for_jwt = json.dumps(data_for_jwt)
        access_token = \
            Authorize.create_access_token(subject=data_for_jwt)
        refresh_token = \
            Authorize.create_refresh_token(subject=data_for_jwt)

        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "REGISTRATION_SUCCESSFULL",
                     "is_supplier": is_supplier}
        )
        Authorize.set_access_cookies(encoded_access_token=access_token,
                                     response=response,
                                     max_age=ACCESS_TOKEN_EXPIRATION_TIME)
        Authorize.set_refresh_cookies(encoded_refresh_token=refresh_token,
                                     response=response,
                                     max_age=REFRESH_TOKEN_EXPIRATION_TIME)
        return response


@register.post("/{user_type}/", 
               summary='WORKS: User registration.', 
               response_model=ResultOut)
async def register_user(user_type: str,
                        user_data: RegisterIn,
                        session: AsyncSession = Depends(get_session)):      
    if user_type not in ['sellers', 'suppliers']:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="INCORRECT_SUBDOMAIN"
        )
    
    is_email_unique = await session.\
        execute(select(User.email).where(User.email.__eq__(user_data.email)))
    is_email_unique = is_email_unique.scalar()
    if is_email_unique:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="EMAIL_EXISTS"
        )

    is_supplier = 1 if user_type == 'suppliers' else 0
    current_datetime = utils.get_moscow_datetime()
    user = User(
        email=user_data.email,
        datetime=current_datetime,
        is_supplier=is_supplier
        )                     
    session.add(user)
    await session.commit()
                
    user_id = await User.get_user_id(user_data.email)
    hashed_password = pwd_hashing.hash_password(password=user_data.password)
    user_creds = UserCreds(
                    user_id=user_id,
                    password=hashed_password
                    )
    if user_type == 'sellers':
        customer = Seller(
                    user_id=user_id
                    ) 
    elif user_type == 'suppliers':
        customer = Supplier(
                    user_id=user_id
                    )
    user_notification = UserNotification(
                            user_id=user_id
                            ) 
    session.add_all((customer, user_creds, user_notification))
    await session.commit()

    if user_type  == 'sellers':
        seller_id = await Seller.get_seller_id(user_id=user_id)
        order = Order(
            seller_id=seller_id,
            datetime=current_datetime
        )
        session.add(order)
        await session.commit()

    encoded_token = utils.create_access_token(user_data.email)
    subject = "Email confirmation"
    recipient = [user_data.email]
    body = CONFIRMATION_BODY.format(host=getenv('APP_URL'),
                                    token=encoded_token)
    await utils.send_email(subject, recipient, body)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "MESSAGE_HAS_BEEN_SENT"}
    )
