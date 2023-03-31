from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import UserObjects, auth_required, get_session
from core.tools import store
from orm import UserCredentialsModel
from schemas import ApplicationResponse, BodyChangePasswordRequest, QueryMyEmailRequest
from schemas import QueryTokenConfirmationRequest as QueryTokenRequest

router = APIRouter()


@router.post(
    path="/change",
    summary="WORKS (need X-CSRF-TOKEN in headers): Change password (token is needed).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: BodyChangePasswordRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    where = UserCredentialsModel.user_id == user.schema.id

    user_credentials = await store.orm.users_credentials.get_one(
        session=session, where=[where]
    )
    if not store.app.pwd.check_hashed_password(
        password=request.old_password, hashed=user_credentials.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password",
        )

    await store.orm.users_credentials.update_one(
        session=session,
        values={
            UserCredentialsModel.password: store.app.pwd.hash_password(
                password=request.new_password
            ),
        },
        where=where,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/forgot",
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
    path="/reset",
    summary="WORKS: reset and change password.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/reset_password",
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
