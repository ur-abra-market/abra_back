from __future__ import annotations

from typing import Final

import httpx
import pytest
from corecrud import Options, Where
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.app import crud
from orm import SupplierModel, UserModel
from typing_ import DictStrAny

SUPPLIER_ID: Final[int] = 1
SELLER_ID: Final[int] = 1


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


@pytest.fixture
def _register_url_seller() -> str:
    return "/register/seller/"


@pytest.fixture
def seller_json() -> DictStrAny:
    return {"email": "morty@example.com", "password": "MortyPassword1!"}


@pytest.fixture(autouse=True)
async def register_seller(
    client: httpx.AsyncClient, _register_url_seller: str, seller_json: DictStrAny
):
    await client.post(url=_register_url_seller, json=seller_json)


@pytest.fixture
async def pure_seller(session: AsyncSession, seller_json: DictStrAny) -> UserModel:
    return await crud.users.select.one(
        Where(UserModel.email == seller_json["email"]),
        session=session,
    )


@pytest.fixture
def _register_url_supplier() -> str:
    return "/register/supplier/"


@pytest.fixture
def supplier_json() -> DictStrAny:
    return {"email": "rick@example.com", "password": "RickPassword1!"}


@pytest.fixture(autouse=True)
async def register_supplier(
    client: httpx.AsyncClient, _register_url_supplier: str, supplier_json: DictStrAny
) -> None:
    await client.post(url=_register_url_supplier, json=supplier_json)


@pytest.fixture
async def pure_supplier(session: AsyncSession, supplier_json: DictStrAny) -> UserModel:
    return await crud.users.select.one(
        Where(UserModel.email == supplier_json["email"]),
        Options(joinedload(UserModel.supplier).joinedload(SupplierModel.company)),
        session=session,
    )


@pytest.fixture
async def supplier_without_company(
    client: httpx.AsyncClient, _login_url: str, supplier_json: DictStrAny
) -> httpx.AsyncClient:
    await _login(client=client, login_url=_login_url, json=supplier_json)

    yield client
