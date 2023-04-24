from __future__ import annotations

from typing import List

import httpx
from starlette import status

from schemas import ApplicationResponse, Category
from tests.endpoints import Route


class TestCategoriesAllRoute(Route[List[Category]]):
    __url__ = "/categories/all/"
    __method__ = "GET"
    __response__ = ApplicationResponse[List[Category]]

    async def test_unauthorized(self, client: httpx.AsyncClient) -> None:
        response, status_code = await self.json_response(client=client)

        assert response.ok
        assert status_code == status.HTTP_200_OK
        assert isinstance(response.result, List)

    async def test_seller(self, seller_client: httpx.AsyncClient) -> None:
        response, status_code = await self.json_response(client=seller_client)

        assert response.ok
        assert status_code == status.HTTP_200_OK
        assert isinstance(response.result, List)

    async def test_supplier(self, supplier_client: httpx.AsyncClient) -> None:
        response, status_code = await self.json_response(client=supplier_client)

        assert response.ok
        assert status_code == status.HTTP_200_OK
        assert isinstance(response.result, List)

    async def test_fail(self) -> None:
        assert False
