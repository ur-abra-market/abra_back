from __future__ import annotations

import httpx
from starlette import status

from tests.endpoints import Route
from typing_ import DictStrAny


class TestSendAccountInfoEndpoint(Route[bool]):
    __url__ = "/register/business/sendInfo/"
    __method__ = "POST"
    __response__ = bool

    async def test_unauthorized_access_failed(self, client: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=client)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_401_UNAUTHORIZED

    async def test_supplier_successfully(
        self,
        supplier: httpx.AsyncClient,
        add_license_data_request: DictStrAny,
        add_company_data_request: DictStrAny,
    ) -> None:
        response, httpx_response = await self.response(
            client=supplier,
            json={
                "supplier_data_request": add_license_data_request,
                "company_data_request": add_company_data_request,
            },
        )

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)

    async def test_seller_access_failed(self, seller: httpx.AsyncClient) -> None:
        response, httpx_response = await self.response(client=seller)

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_404_NOT_FOUND
