from __future__ import annotations

import json

import httpx
from fastapi import UploadFile
from starlette import status

from tests.endpoints import Route
from typing_ import DictStrAny


class TestSendAccountInfoEndpoint(Route[bool]):
    __url__ = "/register/business/sendInfo/"
    __method__ = "POST"
    __response__ = bool

    async def test_unauthorized_access_failed(
        self,
        client: httpx.AsyncClient,
        add_license_data_request: DictStrAny,
        add_company_data_request: DictStrAny,
        add_company_phone_data_request: DictStrAny,
        logo_file: UploadFile,
    ) -> None:
        response, httpx_response = await self.response(
            client=client,
            data={
                "supplier_data_request": json.dumps(add_license_data_request),
                "company_data_request": json.dumps(add_company_data_request),
                "company_phone_data_request": json.dumps(add_company_phone_data_request),
                "logo_image": (logo_file, "logo.png", "application/octet-stream"),
            },
        )

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_401_UNAUTHORIZED

    async def test_seller_access_failed(
        self,
        seller: httpx.AsyncClient,
        add_license_data_request: DictStrAny,
        add_company_data_request: DictStrAny,
        add_company_phone_data_request: DictStrAny,
        logo_file: UploadFile,
    ) -> None:
        response, httpx_response = await self.response(
            client=seller,
            data={
                "supplier_data_request": json.dumps(add_license_data_request),
                "company_data_request": json.dumps(add_company_data_request),
                "company_phone_data_request": json.dumps(add_company_phone_data_request),
                "logo_image": (logo_file, "logo.png", "application/octet-stream"),
            },
        )

        assert not response.ok
        assert httpx_response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response.error, str)
        assert response.error_code == status.HTTP_404_NOT_FOUND

    async def test_supplier_successfully(
        self,
        rick_supplier: httpx.AsyncClient,
        add_license_data_request: DictStrAny,
        add_company_data_request: DictStrAny,
        add_company_phone_data_request: DictStrAny,
        logo_file: UploadFile,
    ) -> None:
        response, httpx_response = await self.response(
            client=rick_supplier,
            data={
                "supplier_data_request": json.dumps(add_license_data_request),
                "company_data_request": json.dumps(add_company_data_request),
                "company_phone_data_request": json.dumps(add_company_phone_data_request),
                "logo_image": (logo_file, "logo.png", "application/octet-stream"),
            },
        )

        assert response.ok
        assert httpx_response.status_code == status.HTTP_200_OK
        assert isinstance(response.result, bool)
