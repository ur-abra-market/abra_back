from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud, fm
from core.depends import UserObjects, auth_required, get_session
from core.security import check_hashed_password, hash_password
from core.settings import application_settings
from orm import ResetTokenModel, UserCredentialsModel
from schemas import (
    ApplicationResponse,
    BodyChangePasswordRequest,
    BodyResetPasswordRequest,
    QueryMyEmailRequest,
)
from schemas import QueryTokenConfirmationRequest as QueryTokenRequest
from typing_ import RouteReturnT

router = APIRouter()


async def change_password_core(session: AsyncSession, user_id: int, password: str) -> None:
    await crud.users_credentials.update.one(
        session=session,
        values={
            UserCredentialsModel.password: hash_password(password=password),
        },
        where=UserCredentialsModel.user_id == user_id,
    )


@router.post(
    path="/change/",
    summary="WORKS (need X-CSRF-TOKEN in headers): Change password (token is needed).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: BodyChangePasswordRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    user_credentials = await crud.users_credentials.by.one(
        session=session,
        user_id=user.schema.id,
    )
    if not check_hashed_password(password=request.old_password, hashed=user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password",
        )

    await change_password_core(
        session=session,
        user_id=user.schema.id,
        password=request.new_password,
    )

    return {
        "ok": True,
        "result": True,
    }


async def check_token_core(session: AsyncSession, token: str) -> bool:
    reset_token = await crud.reset_tokens.by.one(session=session, reset_code=token)
    return reset_token is not None and reset_token.status


@router.get(
    path="/checkToken",
    summary="WORKS: Receive and check token. Next step is /reset-password.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/checkToken",
    description="Moved to GET method /password/checkToken",
    deprecated=True,
    summary="WORKS: Receive and check token. Next step is /password/reset.",
    response_model=ApplicationResponse[bool],
    response_description="Use a GET method",
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
)
@router.post(
    path="/check_for_token/",
    description="Moved to /password/checkToken",
    deprecated=True,
    summary="WORKS: Receive and check token. Next step is /reset_password.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
)
async def check_token(
    query: QueryTokenRequest = Depends(), session: AsyncSession = Depends(get_session)
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await check_token_core(
            session=session,
            token=query.token,
        ),
    }


async def forgot_password_core(session: AsyncSession, user_id: int, email: str) -> ResetTokenModel:
    return await crud.reset_tokens.insert.one(
        session=session,
        values={
            ResetTokenModel.user_id: user_id,
            ResetTokenModel.email: email,
            ResetTokenModel.status: True,
        },
    )


async def send_forgot_mail(email: str, reset_code: str) -> None:
    await fm.send_message(
        message=MessageSchema(
            subject="Reset password",
            recipients=[email],
            template_body={
                "url": application_settings.restore_password,
                "token": reset_code,
            },
            subtype=MessageType.html,
        ),
        template_name="forgot.html.jinja2",
    )


@router.post(
    path="/forgot/",
    summary="WORKS: Send letter with link (token) to user email. Next step is /password/reset.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/forgot_password/",
    description="Moved to /password/forgot",
    deprecated=True,
    summary="WORKS: Send letter with link (token) to user email. Next step is /password/reset_password.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def forgot_password(
    background_tasks: BackgroundTasks,
    request: QueryMyEmailRequest = Depends(),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    user = await crud.users.by.one(session=session, email=request.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email")

    reset_token = await forgot_password_core(session=session, user_id=user.id, email=request.email)
    background_tasks.add_task(
        send_forgot_mail, email=request.email, reset_code=reset_token.reset_code
    )

    return {
        "ok": True,
        "result": True,
    }


async def reset_password_core(
    session: AsyncSession,
    user_id: int,
    reset_token_id: int,
    password: str,
) -> None:
    await crud.users_credentials.update.one(
        session=session,
        values={
            UserCredentialsModel.user_id: user_id,
            UserCredentialsModel.password: hash_password(password=password),
        },
        where=UserCredentialsModel.user_id == user_id,
    )

    await crud.reset_tokens.delete.one(session=session, where=ResetTokenModel.id == reset_token_id)


@router.post(
    path="/reset/",
    summary="WORKS: reset and change password.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/reset_password/",
    description="Moved to /password/reset",
    deprecated=True,
    summary="WORKS: reset and change password.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def reset_password(
    query: QueryTokenRequest = Depends(),
    request: BodyResetPasswordRequest = Body(...),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    reset_token = await crud.reset_tokens.by.one(session=session, reset_code=query.token)
    if not reset_token or not reset_token.status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not now son")

    await reset_password_core(
        session=session,
        user_id=reset_token.user_id,
        reset_token_id=reset_token.id,
        password=request.confirm_password,
    )

    return {
        "ok": True,
        "result": True,
    }
