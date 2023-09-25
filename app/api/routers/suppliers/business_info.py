from typing import Optional

from corecrud import Options, Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SupplierAuthorization
from orm import CompanyModel, CompanyPhoneModel, SupplierModel, UserModel
from schemas import ApplicationResponse, Supplier
from schemas.uploads import (
    CompanyDataUpdateUpload,
    CompanyPhoneDataUpdateUpload,
    SupplierDataUpdateUpload,
)
from typing_ import RouteReturnT

router = APIRouter()


async def update_business_info_core(
    session: AsyncSession,
    user: UserModel,
    supplier_data_request: Optional[SupplierDataUpdateUpload],
    company_data_request: Optional[CompanyDataUpdateUpload],
    company_phone_data_request: Optional[CompanyPhoneDataUpdateUpload],
) -> None:
    if supplier_data_request:
        await crud.suppliers.update.one(
            Values(supplier_data_request.dict()),
            Where(SupplierModel.id == user.supplier.id),
            Returning(SupplierModel.id),
            session=session,
        )

    if company_data_request:
        await crud.companies.update.one(
            Values(company_data_request.dict()),
            Where(CompanyModel.supplier_id == user.supplier.id),
            Returning(CompanyModel.id),
            session=session,
        )

    if company_phone_data_request:
        if not company_phone_data_request.phone_number:
            await crud.companies_phones.delete.one(
                Where(CompanyPhoneModel.company_id == user.supplier.company.id),
                Returning(CompanyPhoneModel.id),
                session=session,
            )
        elif not user.supplier.company.phone:
            await crud.companies_phones.insert.one(
                Values(
                    {
                        **company_phone_data_request.dict(),
                        CompanyPhoneModel.company_id: user.supplier.company.id,
                    }
                ),
                Returning(CompanyPhoneModel),
                session=session,
            )
        else:
            await crud.companies_phones.update.one(
                Values(company_phone_data_request.dict()),
                Where(CompanyPhoneModel.company_id == user.supplier.company.id),
                Returning(CompanyPhoneModel.id),
                session=session,
            )


@router.post(
    path="/update",
    summary="WORKS: update SupplierModel existing information licence information & CompanyModel information",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    supplier_data_request: Optional[SupplierDataUpdateUpload] = Body(None),
    company_data_request: Optional[CompanyDataUpdateUpload] = Body(None),
    company_phone_data_request: Optional[CompanyPhoneDataUpdateUpload] = Body(None),
) -> RouteReturnT:
    await update_business_info_core(
        session=session,
        user=user,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
        company_phone_data_request=company_phone_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_business_info_core(
    session: AsyncSession,
    supplier_id: int,
) -> Supplier:
    return await crud.suppliers.select.one(
        Where(SupplierModel.id == supplier_id),
        Options(
            selectinload(SupplierModel.company).selectinload(CompanyModel.country),
            selectinload(SupplierModel.company)
            .selectinload(CompanyModel.phone)
            .selectinload(CompanyPhoneModel.country),
        ),
        session=session,
    )


@router.get(
    path="",
    summary="WORKS: return company and supplier info",
    response_model=ApplicationResponse[Supplier],
    response_model_exclude={
        "result": {"notifications": ..., "company": {"logo_url"}},
    },
    status_code=status.HTTP_200_OK,
)
async def get_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_business_info_core(session=session, supplier_id=user.supplier.id),
    }