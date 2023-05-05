from typing import Final

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.app import crud
from enums import CurrencyEnum
from orm import UserModel
from typing_ import DictStrAny

COUNTRY_ID: Final[int] = 1
CURRENCY: Final[CurrencyEnum] = CurrencyEnum.RUB


@pytest.fixture
def add_seller_delivery_request() -> DictStrAny:
    return {
        "currency": CURRENCY,
        "country_id": COUNTRY_ID,
    }


@pytest.fixture(scope="session")
def _register_url() -> str:
    return "/register/seller/"


@pytest.fixture(scope="session")
def seller_json() -> DictStrAny:
    return {"email": "morty@example.com", "password": "MortyPassword1!"}


@pytest.fixture(autouse=True, scope="session")
async def register_seller(client: AsyncClient, _register_url: str, seller_json: DictStrAny):
    await client.post(url=_register_url, json=seller_json)


@pytest.fixture(scope="session")
async def pure_seller(session: AsyncSession, seller_json: DictStrAny) -> UserModel:
    return await crud.users.get.one(
        session=session,
        where=[UserModel.email == seller_json["email"]],
    )
