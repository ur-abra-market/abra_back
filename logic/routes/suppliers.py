from classes.response_models import *
from logic import utils
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from database import get_session
from database.models import *
import logging
from fastapi_jwt_auth import AuthJWT


suppliers = APIRouter()


@suppliers.post("/send-account-info/",
                summary="")
async def send_supplier_data_info(user_id: int, # for test
                               supplier_info: SupplierInfo,
                               account_info: SupplierAccountInfo,
                               Authorize: AuthJWT = Depends(),
                               session: AsyncSession = Depends(get_session)) -> JSONResponse:
    # Authorize.jwt_required()
    # user_email = Authorize.get_jwt_subject()
    # user_id = await User.get_user_id(email=user_email)
    await session.execute(update(User)\
                          .where(User.id.__eq__(user_id))\
                          .values(first_name=supplier_info.first_name,
                                  last_name=supplier_info.last_name,
                                  phone=supplier_info.phone))
    await session.commit()
    supplier_data: UserAdress = UserAdress(user_id=user_id,
                               country=supplier_info.country)
    session.add(supplier_data)
    await session.commit()
    await session.execute(update(Supplier)\
                          .where(Supplier.user_id.__eq__(user_id))\
                          .values(license_number=supplier_info.tax_number))
    await session.commit()
    supplier_id: int = await session.execute(
        select(Supplier.id)\
        .where(Supplier.user_id.__eq__(user_id))
    )
    supplier_id: int = supplier_id.scalar()
    account_data: Company = Company(
        supplier_id=supplier_id,
        
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "DATA_HAS_BEEN_SENT"}
    )
