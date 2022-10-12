from app.classes.response_models import *
from app.logic.consts import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.database.models import *


users = APIRouter()


@users.get("/latest_searches/",
           summary='WORKS (example 5): Get latest searches by user_id.',
           response_model=SearchesOut)
async def get_latest_searches_for_user(user_id: int, 
                                session: AsyncSession = Depends(get_session)):
    searches =  await session.\
                execute(select(UserSearch.search_query, UserSearch.datetime).\
                where(UserSearch.user_id.__eq__(user_id)))
    searches = [dict(search_query=row[0], datetime=str(row[1]))\
                for row in searches if searches]
                    
    if searches:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": searches}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_SEARCHES"
        )
