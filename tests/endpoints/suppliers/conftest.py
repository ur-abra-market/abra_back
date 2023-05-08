from typing import Final, List

import pytest

from typing_ import DictStrAny

CATEGORY_ID: Final[int] = 1
PROPERTIES: Final[List[int]] = [1, 1]
VARIATIONS: Final[List[int]] = [3, 4]


@pytest.fixture
def add_product_request() -> DictStrAny:
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
