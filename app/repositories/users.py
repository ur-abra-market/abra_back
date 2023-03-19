from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.schemas import UserSchema
from app.common import exceptions


class UserRepo:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> UserSchema:
        user_query = select(User).filter(User.email == email)
        user_data = await session.execute(user_query)
        user = user_data.scalar()
        if not user:
            return
            # raise exceptions.NotFoundException(message='User not found')
        return UserSchema(
            user_id=user.id, email=user.email, is_supplier=user.is_supplier
        )


user_repo = UserRepo()
