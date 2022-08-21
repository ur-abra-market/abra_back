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


@suppliers.post("/send-account-info/",
                summary="")
async def view_fill_data_field(supplier_info: SupplierAccountInfoIn,
                               session: AsyncSession = Depends(get_session)):
    user_info = User(
        first_name=supplier_info.first_name,
        last_name=supplier_info.last_name
    )
    