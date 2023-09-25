from corecrud import (
    Options,
    Returning,
    Values,
    Where,
)
from fastapi import APIRouter
from fastapi.param_functions import Body
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from core.depends import AuthJWT, Authorization, DatabaseSession
from orm import UserModel
from schemas import ApplicationResponse, User
from schemas.uploads import (
    ChangeEmailUpload,
    UserDataUpdateUpload,
)
from typing_ import RouteReturnT
from utils.cookies import unset_jwt_cookies

router = APIRouter()


async def delete_account_core(session: AsyncSession, user_id: int) -> None:
    await crud.users.update.one(
        Values({UserModel.is_deleted: True}),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.delete(
    path="/delete",
    summary="WORKS: Delete user account.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_account(
    response: Response,
    authorize: AuthJWT,
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    await delete_account_core(session=session, user_id=user.id)
    unset_jwt_cookies(response=response, authorize=authorize)

    return {
        "ok": True,
        "result": True,
    }


async def get_personal_info_core(session: AsyncSession, user_id: int) -> UserModel:
    return await crud.users.select.one(
        Where(UserModel.id == user_id),
        Options(joinedload(UserModel.country)),
        session=session,
    )


@router.get(
    path="/personalInfo",
    summary="WORKS: get UserModel information such as: first_name, last_name, country_code, phone_number, country_data",
    response_model=ApplicationResponse[User],
    response_model_exclude={
        "result": {
            "admin",
            "seller",
            "supplier",
        },
    },
    status_code=status.HTTP_200_OK,
)
async def get_personal_info(user: Authorization, session: DatabaseSession) -> RouteReturnT:
    return {"ok": True, "result": await get_personal_info_core(session=session, user_id=user.id)}


async def update_account_info_core(
    session: AsyncSession,
    user_id: int,
    request: UserDataUpdateUpload,
) -> None:
    await crud.users.update.one(
        Values(request.dict()),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.post(
    path="/personalInfo/update",
    summary="WORKS: updated UserModel information such as: first_name, last_name, country_code, phone_number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_account_info(
    user: Authorization,
    session: DatabaseSession,
    request: UserDataUpdateUpload = Body(...),
) -> RouteReturnT:
    await update_account_info_core(session=session, user_id=user.id, request=request)

    return {
        "ok": True,
        "result": True,
    }


async def change_email_core(
    session: AsyncSession,
    user_id: int,
    email: str,
) -> None:
    await crud.users.update.one(
        Values(
            {
                UserModel.email: email,
            }
        ),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.post(
    path="/changeEmail",
    summary="WORKS: allows user to change his email",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_email(
    user: Authorization,
    session: DatabaseSession,
    request: ChangeEmailUpload = Body(...),
) -> RouteReturnT:
    await change_email_core(
        session=session,
        user_id=user.id,
        email=request.confirm_email,
    )

    return {
        "ok": True,
        "result": True,
    }
