from __future__ import annotations

from typing import Any, Dict

import httpx
from starlette import status

from tests.endpoints import Route


class TestSellerDeliveryEndpoint(Route[bool]):
    __url__ = "/sellers/delivery/"
    __method__ = "POST"
    __response__ = bool

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

    async def test_seller_successfully(
        self, seller: httpx.AsyncClient, add_seller_delivery_request: Dict[str, Any]
    ) -> None:
        response, httpx_response = await self.response(client=seller, json=add_seller_delivery_request)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_201_CREATED
        assert isinstance(response.result, bool)
