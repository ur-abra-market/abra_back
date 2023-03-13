from app.classes.response_models import ResultOut
from pydantic import BaseModel, EmailStr
from app.logic import utils
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.logic.consts import *
from app.logic.queries import *
from app.database import get_session
from app.database import models
from app.logic import pwd_hashing
import logging
from os import getenv
import re


class ConfirmationToken(BaseModel):
    token: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


register = APIRouter()


@register.post(
    "/email_confirmation_result/",
    summary="WORKS: Processing token that was sent to user "
    "during the registration process.",
    response_model=ResultOut,
)
async def receive_confirmation_result(
    token: ConfirmationToken, session: AsyncSession = Depends(get_session)
):
    try:
        decoded_token = utils.get_current_user(token.token)
        decoded_token = decoded_token.split("'")
        logging.info(decoded_token)
        existing_email = await session.execute(
            select(models.User.email).where(models.User.email.__eq__(decoded_token[0]))
        )
        existing_email = existing_email.scalar()
    # bad practice - catch just Exception. Which exactly error should be catched here?
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_TOKEN"
        )

    if existing_email:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "REGISTRATION_SUCCESSFUL"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_FOUND"
        )


@register.post(
    "/{user_type}/", summary="WORKS: User registration.", response_model=ResultOut
)
async def register_user(
    user_type: str, user_data: RegisterIn, session: AsyncSession = Depends(get_session)
):
    if user_type not in ["sellers", "suppliers"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="INCORRECT_SUBDOMAIN"
        )

    email_pattern = (
        r"([A-Za-z0-9]+[!#$%&'*+/=?^_`|~-]*[.]?)*[A-Za-z0-9]+@[a-z0-9-]+(\.[a-z]{2,})+"
    )
    if not re.fullmatch(email_pattern, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="EMAIL_VALIDATION_ERROR"
        )

    password_pattern = r"(?=.*[0-9])(?=.*[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}"
    if not re.fullmatch(password_pattern, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="PASSWORD_VALIDATION_ERROR",
        )

    is_email_unique = await session.execute(
        select(models.User.email).where(models.User.email.__eq__(user_data.email))
    )
    is_email_unique = is_email_unique.scalar()
    if is_email_unique:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="EMAIL_EXISTS"
        )

    is_supplier = 1 if user_type == "suppliers" else 0
    current_datetime = utils.get_moscow_datetime()
    user = models.User(
        email=user_data.email, datetime=current_datetime, is_supplier=is_supplier
    )
    session.add(user)
    await session.commit()

    user_id = await models.User.get_user_id(user_data.email)
    hashed_password = pwd_hashing.hash_password(password=user_data.password)
    user_creds = models.UserCred(user_id=user_id, password=hashed_password)
    if user_type == "sellers":
        customer = models.Seller(user_id=user_id)
    elif user_type == "suppliers":
        customer = models.Supplier(user_id=user_id)
    user_notification = models.UserNotification(user_id=user_id)

    session.add_all((customer, user_creds, user_notification))
    await session.commit()
    await session.flush()
    await session.refresh(customer)

    if user_type == "sellers":
        #TODO: use refreshed customer.id instead of that request
        seller_id = await models.Seller.get_seller_id(user_id=user_id)
        order = models.Order(seller_id=seller_id, datetime=current_datetime)
        image = models.SellerImage(seller_id=seller_id, thumbnail_url=None, source_url=None)
        session.add_all((order, image))
        await session.commit()
    elif user_type == "suppliers":
        logging.info("ADDING COMPANY: %s", customer.id)
        company = models.Company(supplier_id=customer.id)
        session.add(company)
        await session.commit()

    encoded_token = utils.create_access_token(user_data.email)
    subject = "Email confirmation"
    recipient = [user_data.email]
    body = CONFIRMATION_BODY.format(host=getenv("APP_URL"), token=encoded_token)
    logging.info(["TOKEN", encoded_token])
    await utils.send_email(subject, recipient, body)

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": "MESSAGE_HAS_BEEN_SENT"}
    )
