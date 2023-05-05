from typing import Any, Dict, Final, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.app import crud
from orm import SupplierModel, UserModel
from typing_ import DictStrAny

CATEGORY_ID: Final[int] = 1
PROPERTIES: Final[List[int]] = [1, 1]
VARIATIONS: Final[List[int]] = [3, 4]


@pytest.fixture
def add_product_request() -> Dict[str, Any]:
    return {
        "name": "Test Product",
        "description": "This is a test product",
        "category_id": CATEGORY_ID,
        "properties": PROPERTIES,
        "variations": VARIATIONS,
        "prices": [
            {
                "value": 9.99,
                "min_quantity": 1,
                "discount": 0,
            },
        ],
    }


@pytest.fixture(scope="session")
def _register_url() -> str:
    return "/register/supplier/"


@pytest.fixture(scope="session")
def supplier_json() -> DictStrAny:
    return {"email": "rick@example.com", "password": "RickPassword1!"}


@pytest.fixture(autouse=True, scope="session")
async def register_supplier(client: AsyncClient, _register_url: str, supplier_json: DictStrAny):
    await client.post(url=_register_url, json=supplier_json)


@pytest.fixture(scope="session")
async def pure_supplier(session: AsyncSession, supplier_json: DictStrAny) -> UserModel:
    return await crud.users.get.one(
        session=session,
        where=[UserModel.email == supplier_json["email"]],
        options=[joinedload(UserModel.supplier).joinedload(SupplierModel.company)],
    )
