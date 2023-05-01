from __future__ import annotations

import httpx
from starlette import status

from app.schemas import Product
from tests.endpoints import Route

class TestAddProductEndpoint(Route[Product]):
    __url__ = "/addProduct/"
    __method__ = "POST"
    __response__ = Product


    async def test_unathorised_access_denied(self, client: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=client)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response.error, str) 
        assert response.error_code == status.HTTP_404_NOT_FOUND

    async def test_seller_access_denied(self, seller: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=seller)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response.error, str) 
        assert response.error_code == status.HTTP_404_NOT_FOUND