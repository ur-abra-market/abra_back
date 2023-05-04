from typing import Final

import pytest

from enums import CurrencyEnum
from typing_ import DictStrAny

COUNTRY_ID: Final[int] = 1
CURRENCY: Final[CurrencyEnum] = CurrencyEnum.RUB


@pytest.fixture
def add_seller_delivery_request() -> DictStrAny:
    return {
        "currency": CURRENCY,
        "country_id": COUNTRY_ID,
    }
