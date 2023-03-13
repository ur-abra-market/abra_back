import json
from typing import Optional

from fastapi import Depends
from fastapi_jwt_auth import AuthJWT

from app.repositories import user_repo
from app.schemas import UserSchema
from app.common.exceptions import AuthException

class AuthenticateService:
    def __init__(self, user_repo):
        self._repo = user_repo


    def auth_required(self, auth: AuthJWT = Depends()):
        auth.jwt_optional()
        user_raw_data = auth.get_jwt_subject()
        if not user_raw_data:
            raise AuthException(message='Authentication required')

        user_data = json.loads(user_raw_data)
        user_modeled = UserSchema(**user_data)
        return user_modeled

    def auth_optional(self, auth: AuthJWT = Depends())->Optional[UserSchema]:
        auth.jwt_optional()
        user_raw_data = auth.get_jwt_subject()
        if user_raw_data:
            user_data = json.loads(user_raw_data)
            user_modeled = UserSchema(**user_data)
            return user_modeled


auth_service = AuthenticateService(user_repo)
