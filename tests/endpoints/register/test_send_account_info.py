from __future__ import annotations

import httpx
from starlette import status

from tests.endpoints import Route
from typing_ import DictStrAny


class TestSendAccountInfoEndpoint(Route[bool]):
    __url__ = "/register/account/sendInfo"
    __method__ = "POST"
    __response__ = bool

    async def test_unauthorized_access_failed(
        self, client: httpx.AsyncClient, add_account_info_request: DictStrAny
    ) -> None:
        response, httpx_response = await self.response(
            client=client, json=add_account_info_request
        )

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_401_UNAUTHORIZED

    async def test_supplier_successfully(
        self, supplier: httpx.AsyncClient, add_account_info_request: DictStrAny
    ) -> None:
        response, httpx_response = await self.response(
            client=supplier, json=add_account_info_request
        )

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)

    async def test_seller_successfully(
        self, supplier: httpx.AsyncClient, add_account_info_request: DictStrAny
    ) -> None:
        response, httpx_response = await self.response(
            client=supplier, json=add_account_info_request
        )

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)
