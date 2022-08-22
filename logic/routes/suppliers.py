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


suppliers = APIRouter()


@suppliers.post("/{user_id}/send-account-info/",
                summary="")
async def view_fill_data_field(user_id: int,
                               supplier_info: SupplierAccountInfoIn,
                               session: AsyncSession = Depends(get_session)):
    # do we need to check user_id in suppliers table?
    await session.execute(update(User)\
                          .where(User.id.__eq__(user_id))\
                          .values(first_name=supplier_info.first_name,
                                  last_name=supplier_info.last_name,
                                  phone=supplier_info.phone))
    await session.commit()
    # supplier_data = UserAdress(user_id=user_id,
    #                        country=supplier_info.country)
    # session.add(supplier_data)
    # await session.commit()
    await session.execute(update(Supplier)\
                          .where(Supplier.user_id.__eq__(user_id))\
                          .values(license_number=supplier_info.tax_number))
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "DATA_HAS_BEEN_SENT"}
    )

    