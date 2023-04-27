from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI

from typing_ import DictStrAny


@pytest.fixture
async def client(app: FastAPI) -> httpx.AsyncClient:
    BASE_URL = "http://testserver"

    async with httpx.AsyncClient(app=app, base_url=BASE_URL) as _client:
        yield _client


@pytest.fixture
def _login_url() -> str:
    return "/login/"


async def _login(
    client: httpx.AsyncClient,
    login_url: str,
    json: DictStrAny,
) -> None:
    await client.post(url=login_url, json=json)


@pytest.fixture
def _seller_register_url() -> str:
    return "/register/seller/"


@pytest.fixture
def _seller_json() -> DictStrAny:
    return {"email": "patrick.seller@email.com", "password": "Patrick_password1"}


@pytest.fixture(autouse=True)
async def _seller(
    client: httpx.AsyncClient,
    _seller_register_url: str,
    _seller_json: DictStrAny,
) -> None:
    await client.post(url=_seller_register_url, json=_seller_json)


@pytest.fixture
async def seller(
    client: httpx.AsyncClient, _login_url: str, _seller_json: DictStrAny
) -> httpx.AsyncClient:
    await _login(client=client, login_url=_login_url, json=_seller_json)

    yield client


@pytest.fixture
def _supplier_register_url() -> str:
    return "/register/supplier/"


@pytest.fixture
def _supplier_json() -> DictStrAny:
    return {"email": "spongebob.supplier@email.com", "password": "Spongebob_password1"}


@pytest.fixture(autouse=True)
async def _supplier(
    client: httpx.AsyncClient,
    _supplier_register_url: str,
    _supplier_json: DictStrAny,
) -> None:
    await client.post(url=_supplier_register_url, json=_supplier_json)


@pytest.fixture
async def supplier(
    client: httpx.AsyncClient, _login_url: str, _supplier_json: DictStrAny
) -> httpx.AsyncClient:
    await _login(client=client, login_url=_login_url, json=_supplier_json)

    yield client
