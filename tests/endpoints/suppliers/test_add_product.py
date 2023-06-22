from __future__ import annotations

import httpx
from starlette import status

from schemas import Product
from tests.endpoints import Route
from typing_ import DictStrAny


class TestAddProductEndpoint(Route[Product]):
    __url__ = "/suppliers/addProduct/"
    __method__ = "POST"
    __response__ = Product

    async def test_unauthorized_access_failed(
        self, client: httpx.AsyncClient, add_product_request: DictStrAny
    ) -> None:
        response, httpx_response = await self.response(client=client, json=add_product_request)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_401_UNAUTHORIZED

    async def test_seller_access_failed(
        self, seller: httpx.AsyncClient, add_product_request: DictStrAny
    ) -> None:
        response, httpx_response = await self.response(client=seller, json=add_product_request)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_404_NOT_FOUND

    async def test_supplier_successfully(
        self, supplier: httpx.AsyncClient, add_product_request: DictStrAny
    ) -> None:
        response, httpx_response = await self.response(client=supplier, json=add_product_request)

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, Product)
