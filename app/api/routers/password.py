from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import UserObjects, auth_required, get_session
from core.security import check_hashed_password, hash_password
from core.tools import tools
from orm import UserCredentialsModel
from schemas import ApplicationResponse, BodyChangePasswordRequest, QueryMyEmailRequest
from schemas import QueryTokenConfirmationRequest as QueryTokenRequest

router = APIRouter()


async def change_password_core(session: AsyncSession, user_id: int, password: str) -> None:
    await tools.store.orm.users_credentials.update_one(
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
) -> ApplicationResponse[bool]:
    user_credentials = await tools.store.orm.users_credentials.get_one(
        session=session, where=[UserCredentialsModel.user_id == user.schema.id]
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
    request: QueryMyEmailRequest, session: AsyncSession = Depends(get_session)
) -> ApplicationResponse[bool]:
    return {"ok": False, "detail": "Not worked yet..."}


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
    request: BodyChangePasswordRequest = Body(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    return {"ok": False, "detail": "Not worked yet..."}
