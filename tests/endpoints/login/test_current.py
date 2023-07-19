from __future__ import annotations

import httpx
from starlette import status

from schemas import User
from tests.endpoints import Route


class TestCurrentRoute(Route[User]):
    __url__ = "auth/login/current"
    __method__ = "GET"
    __response__ = User

    async def test_unauthorized_failed(self, client: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=client)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_401_UNAUTHORIZED

    async def test_seller_successfully(self, seller: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=seller)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, User) and response.result.seller

    async def test_supplier_successfully(self, supplier: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=supplier)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, User) and response.result.supplier
