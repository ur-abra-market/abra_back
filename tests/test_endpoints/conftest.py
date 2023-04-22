from __future__ import annotations

from typing import Any, Dict

import httpx
import pytest
from fastapi import FastAPI


@pytest.fixture(scope="session")
async def client(app: FastAPI) -> httpx.AsyncClient:
    async with httpx.AsyncClient(app=app, base_url="http://test") as _client:
        yield _client


@pytest.fixture(scope="session")
def seller() -> Dict[str, Any]:
    return {
        "email": "chupapa_seller@email.com",
        "password": "strongest_password_in_the_bikini_bottom",
    }


@pytest.fixture(scope="session")
async def create_seller_user(
    client: httpx.AsyncClient, seller: Dict[str, Any]
) -> httpx.AsyncClient:
    await client.post(url="/register/seller", json=seller)

    yield client


@pytest.fixture(scope="session")
async def seller_client(
    create_seller_user: httpx.AsyncClient, seller: Dict[str, Any]
) -> httpx.AsyncClient:
    await create_seller_user.post(url="/login", json=seller)

    yield create_seller_user


@pytest.fixture(scope="session")
def supplier() -> Dict[str, Any]:
    return {
        "email": "chupapa_supplier@email.com",
        "password": "strongest_password_in_the_bikini_bottom",
    }


@pytest.fixture(scope="session")
async def create_supplier_user(
    client: httpx.AsyncClient, supplier: Dict[str, Any]
) -> httpx.AsyncClient:
    await client.post(url="/register/supplier/", json=supplier)

    yield client


@pytest.fixture(scope="session")
async def supplier_client(
    create_supplier_user: httpx.AsyncClient, supplier: Dict[str, Any]
) -> httpx.AsyncClient:
    await create_supplier_user.post(url="/login/", json=supplier)

    yield create_supplier_user
