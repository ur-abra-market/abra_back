from typing import Final

import pytest

from typing_ import DictStrAny

FIRST_NAME: Final[str] = "First Name"
LAST_NAME: Final[str] = "Last Name"
PHONE_COUNTRY_CODE: Final[str] = "+7"
PHONE_COUNTRY: Final[str] = "9164049883"
LICENSE_NUMBER: Final[str] = "123456"
COMPANY_NAME: Final[str] = "Company Name"
YEAR_ESTABLISHED: Final[int] = 1995
NUMBER_EMPLOYEES: Final[int] = 15
COMPANY_DESCRIPTION: Final[str] = "Description"
ADDRESS: Final[str] = "Address"
LOGO_URL: Final[str] = "logo.png"
BUSINESS_SECTOR: Final[str] = "Clothing"
BUSINESS_EMAIL: Final[str] = "company.email@example.com"


@pytest.fixture
def add_account_info_request() -> DictStrAny:
    return {
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "phone_country_code": PHONE_COUNTRY_CODE,
        "phone_number": PHONE_COUNTRY,
    }


@pytest.fixture
def add_license_data_request() -> DictStrAny:
    return {"license_number": LICENSE_NUMBER}


@pytest.fixture
def add_company_data_request() -> DictStrAny:
    return {
        "phone_country_code": PHONE_COUNTRY_CODE,
        "phone_number": PHONE_COUNTRY,
        "name": COMPANY_NAME,
        "is_manufacturer": False,
        "year_established": YEAR_ESTABLISHED,
        "number_employees": NUMBER_EMPLOYEES,
        "description": COMPANY_DESCRIPTION,
        "address": ADDRESS,
        "logo_url": LOGO_URL,
        "business_sector": BUSINESS_SECTOR,
        "business_email": BUSINESS_EMAIL,
    }
