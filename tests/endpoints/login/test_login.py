from __future__ import annotations

import httpx
import pytest
from starlette import status

from tests.endpoints import Route
from typing_ import DictStrAny


class TestLoginRoute(Route[bool]):
    __url__ = "/login/"
    __method__ = "POST"
    __response__ = bool

    @pytest.mark.parametrize(
        "credentials",
        [
            {  # invalid email and password
                "email": "invalid@email.com",
                "password": "invalidPassword1q!",
            },
            {  # invalid password
                "email": "patrick.seller@email.com",
                "password": "invalidPassword1q!",
            },
            {  # invalid email
                "email": "patrick.seller@email.com",
                "password": "strongest_password_in_the_bikini_bottom1Q!",
            },
        ],
    )
    async def test_unauthorized_with_invalid_credentials_failed(
        self,
        client: httpx.AsyncClient,
        credentials: DictStrAny,
    ) -> None:
        response, httpx_response = await self.response(client=client, json=credentials)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_403_FORBIDDEN
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_403_FORBIDDEN
