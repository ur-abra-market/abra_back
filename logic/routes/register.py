from classes.response_models import *
from logic import utils
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from database import get_session
from database.models import *
from logic import pwd_hashing
import logging


register = APIRouter()
   

@register.post("/email-confirmation/")
async def send_confirmation_letter(email: MyEmail) -> JSONResponse:
    encoded_token = utils.create_access_token(email)
    subject = "Email confirmation"
    recipient = [email.email]
    body = CONFIRMATION_BODY.format(token=encoded_token)
    await utils.send_email(subject, recipient, body)
    return JSONResponse(
        status_code=200,
        content={"result": "Message has been sent"}
    )


@register.post("/email-confirmation-result/")
async def receive_confirmation_result(token: ConfirmationToken,
                                session: AsyncSession = Depends(get_session)):
    try:
        decoded_token = utils.get_current_user(token.token)
        decoded_token = decoded_token.split("'")
        existing_email = await session\
                        .execute(select(User.email)\
                        .where(User.email.__eq__(decoded_token[1])))
        existing_email = existing_email.scalar()
        if existing_email:
            return JSONResponse(
                status_code=200,
                content={"result": "Registration successful."}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


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

    current_datetime = utils.get_moscow_datetime()
    user = User(
        email=user_data.email,
        datetime=current_datetime
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
    session.add_all((customer, user_creds))
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "REGISTRATION_SUCCESSFUL"}
    )
