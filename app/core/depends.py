from typing import Optional

from fastapi import Depends, Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from core.tools import store
from orm.core import async_sessionmaker
from schemas import JWT, User

__all__ = (
    "get_session",
    "auth_required",
    "auth_optional",
)


async def get_session() -> AsyncSession:
    async with async_sessionmaker.begin() as _session:
        yield _session


def get_jwt_subject(authorize: AuthJWT) -> JWT:
    subject = authorize.get_jwt_subject()
    return JWT() if subject is None else JWT.parse_raw(subject)


async def auth_core(authorize: AuthJWT, session: AsyncSession) -> Optional[User]:
    jwt = get_jwt_subject(authorize=authorize)

    user = await store.orm.users.get_by_id(
        session=session,
        id=jwt.user_id,
    )
    return user


async def auth_required(
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> User:
    authorize.jwt_required()

    user = await auth_core(authorize=authorize, session=session)
    return User.from_orm(user)


async def auth_optional(
    authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    authorize.jwt_optional()

    user = await auth_core(authorize=authorize, session=session)
    return None if user is None else User.from_orm(user)


async def auth_mock(
    request: Request,
):
    class MockUser:
        def __init__(self) -> None:
            self.id = 111

    user = MockUser()
    request.state.user_profile = user
    return user
