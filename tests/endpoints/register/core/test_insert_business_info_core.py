from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.register import send_business_info_core
from orm import UserModel
from schemas import BodyCompanyDataRequest, BodySupplierDataRequest, Supplier
from typing_ import DictStrAny


async def test_send_account_info_core(
    session: AsyncSession,
    add_license_data_request: DictStrAny,
    add_company_data_request: DictStrAny,
    pure_supplier: UserModel,
) -> None:
    supplier = Supplier.from_orm(pure_supplier)

    supplier_request = BodySupplierDataRequest.parse_obj(add_license_data_request)
    company_request = BodyCompanyDataRequest.parse_obj(add_company_data_request)

    await send_business_info_core(
        session=session,
        supplier_data_request=supplier_request,
        company_data_request=company_request,
        supplier_id=supplier.id,
    )

    assert (
        supplier.dict().items() <= supplier_request.dict().items()
        and supplier.company.dict().items() <= company_request.dict().items()
    )
