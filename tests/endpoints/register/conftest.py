from __future__ import annotations

from io import BytesIO
from typing import Final

import pytest
from fastapi import UploadFile

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
BUSINESS_SECTOR: Final[str] = "Clothing"
BUSINESS_EMAIL: Final[str] = "company.email@example.com"
COUNTRY_ID: Final[int] = 1


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
        "name": COMPANY_NAME,
        "is_manufacturer": False,
        "year_established": YEAR_ESTABLISHED,
        "employees_number": NUMBER_EMPLOYEES,
        "description": COMPANY_DESCRIPTION,
        "address": ADDRESS,
        "business_sector": BUSINESS_SECTOR,
        "business_email": BUSINESS_EMAIL,
        "country_id": COUNTRY_ID,
    }


@pytest.fixture
def add_company_phone_data_request() -> DictStrAny:
    return {
        "phone_number": PHONE_COUNTRY,
        "country_id": COUNTRY_ID,
    }


@pytest.fixture
def logo_file() -> UploadFile:
    file_content = BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\xdac\xfc\xcf\xc0P\x0f\x00\x04\x85\x01\x80\x84\xa9\x8c!\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return UploadFile(file=file_content, filename="logo.png")
