from __future__ import annotations

import httpx
from starlette import status

from tests.endpoints import Route


class TestRootRoute(Route[bool]):
    __url__ = "/"
    __method__ = "GET"
    __response__ = bool

    async def test_unauthorized_successfully(self, client: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=client)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)

    async def test_seller_successfully(self, seller: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=seller)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)

    async def test_supplier_successfully(self, supplier: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=supplier)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)
