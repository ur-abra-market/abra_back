from __future__ import annotations

from typing import List

import httpx
from starlette import status

from schemas import Order
from tests.endpoints import Route


class TestOrdersEndpoint(Route[List[Order]]):
    __url__ = "/sellers/orders/"
    __method__ = "GET"
    __response__ = List[Order]

    async def test_unauthorized_access_failed(self, client: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=client)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_401_UNAUTHORIZED

    async def test_supplier_access_failed(self, supplier: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=supplier)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_404_NOT_FOUND

    async def test_seller_successfully(self, seller: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=seller)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, List)
