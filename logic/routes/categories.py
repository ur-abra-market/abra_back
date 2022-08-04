from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from logic.consts import *
from classes.response_models import *
from sqlalchemy import text
from re import fullmatch


categories = APIRouter()


@categories.get("/path", 
    summary='WORKS (example "stove"): Get category path (route) by its name.',
    response_model=CategoryPath)
async def get_category_path(category: str, 
                            session: AsyncSession = Depends(get_session)):
    category_pattern = r'^[A-Za-z0-9\_]+$'
    if not fullmatch(category_pattern, category):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="INVALID_CATEGORY"
        )
    category_path = await session\
        .execute(SQL_QUERY_FOR_CATEGORY_PATH.format(category))
    category_path = category_path.scalar()
    if category_path:
        return JSONResponse(
            status_code=200,
            content={"result": category_path}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )
