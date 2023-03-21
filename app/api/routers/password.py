from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import auth_required, get_session
from core.tools import store
from orm import UserCredentialsModel
from schemas import ApplicationResponse, ChangePassword, User

router = APIRouter()


@router.post(
    path="/change",
    summary="WORKS (need X-CSRF-TOKEN in headers): Change password (token is needed).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: ChangePassword = Body(...),
    user: User = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    where = [
        UserCredentialsModel.user_id == user.id,
    ]

    credentials = await store.orm.users_credentials.get_one(session=session, where=where)
    if store.app.pwd.check_hashed_password(
        password=request.old_password, hashed=credentials.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Old password do not match"
        )

    await store.orm.users_credentials.update(
        session=session,
        values={
            "password": store.app.pwd.hash_password(request.new_password),
        },
        where=where,
    )

    return {
        "ok": True,
        "result": True,
    }
