from __future__ import annotations

from typing import Final

import httpx
import pytest
from fastapi import FastAPI

from typing_ import DictStrAny

SUPPLIER_ID: Final[int] = 1
SELLER_ID: Final[int] = 2


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
def _seller_json() -> DictStrAny:
    return {"email": "seller@mail.ru", "password": "Password1!"}


@pytest.fixture
async def seller(
    client: httpx.AsyncClient, _login_url: str, _seller_json: DictStrAny
) -> httpx.AsyncClient:
    await _login(client=client, login_url=_login_url, json=_seller_json)

    yield client


@pytest.fixture
def seller_id() -> int:
    return SELLER_ID


@pytest.fixture
def _supplier_json() -> DictStrAny:
    return {"email": "supplier@mail.ru", "password": "Password1!"}


@pytest.fixture
async def supplier(
    client: httpx.AsyncClient, _login_url: str, _supplier_json: DictStrAny
) -> httpx.AsyncClient:
    await _login(client=client, login_url=_login_url, json=_supplier_json)

    yield client


@pytest.fixture
def supplier_id() -> int:
    return SUPPLIER_ID
