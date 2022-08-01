from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from logic.consts import *
from classes.response_models import *


categories = APIRouter()


@categories.get("/path", summary='WORKS (example "stove"): Get category path (route) by its name.',
                response_model=CategoryPath)
async def get_category_path(category: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        SQL_QUERY_FOR_CATEGORY_PATH, {'category_name': category}
    )
    result = result.all()

    if result:
        return JSONResponse(
            status_code=200,
            content={"result": result[0]}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )
