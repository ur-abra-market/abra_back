from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import get_session
from core.tools import store
from enums import UserType
from orm import UserModel
from schemas import ApplicationResponse, Register

router = APIRouter()


@router.post(
    path="/{user_type}",
    summary="WORKS: User registration.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def register_user(
    user_type: UserType = Path(...),
    request: Register = Body(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse:
    exists = await store.orm.users.get_one(
        session=session,
        where=[
            UserModel.email == request.email,
        ],
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with current email already registered",
        )

    user = await store.orm.users.insert(
        session=session,
        values={
            "email": request.email,
            "is_supplier": user_type == UserType.SUPPLIER,
        },
    )
    await store.orm.users_credentials.insert(
        session=session,
        values={
            "user_id": user.id,
            "password": store.app.pwd.hash_password(password=request.password),
        },
    )

    return {
        "ok": True,
        "result": True,
    }
