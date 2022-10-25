import json
from app.classes.response_models import *
from app.logic.consts import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.database.models import *


users = APIRouter()


@users.get("/get_role",
           summary="get user role",
           response_model=GetRoleOut)
async def get_user_role(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())['email']
    if user_email:
        is_supplier = await User.get_user_role(email=user_email)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"is_supplier": is_supplier}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_SEARCHES"
        )


@users.get("/latest_searches/",
           summary='WORKS (example 5): Get latest searches by user_id.',
           response_model=SearchesOut)
async def get_latest_searches_for_user(user_id: int,
                                       session: AsyncSession = Depends(get_session)):
    searches = await session.\
        execute(select(UserSearch.search_query, UserSearch.datetime).
                where(UserSearch.user_id.__eq__(user_id)))
    searches = [dict(search_query=row[0], datetime=str(row[1]))
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
