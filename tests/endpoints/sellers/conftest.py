from typing import Any, Dict, Final

import pytest

from enums import CurrencyEmum

COUNTRY_ID: Final[int] = 1
CURRENCY: Final[CurrencyEmum] = CurrencyEmum.RUB

@pytest.fixture
def add_seller_delivery_request() -> Dict[str, Any]:
    return{
        "currency": CURRENCY,
        "country_id": COUNTRY_ID
    }