from datetime import datetime, timezone
from typing import List, Any

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, join
from starlette import status

from core.depends import UserObjects, auth_required, auth_required_supplier, get_session
from core.tools import store
from orm import (
    UserModel,
    CompanyModel,
    SupplierModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationValueModel,
)

from schemas import (
    ApplicationResponse,
    SuppliersProductsResponse,
    BodyProductUploadRequest,
)

router = APIRouter()


@router.get("/get_supplier_info")
async def get_supplier_info(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
):

    await store.orm.users.get_one(
        SupplierModel,
        CompanyModel,
        session=session,
        where=[UserModel.id == user.schema.id],
        join=[
            [SupplierModel, SupplierModel.user_id == UserModel.id],
            [CompanyModel, CompanyModel.supplier_id == SupplierModel.id],
        ],
        options=[joinedload(UserModel.supplier.company)]
        # select_from=[
        #   join(CompanyModel, SupplierModel, CompanyModel.supplier_id == SupplierModel.id)
        # ]
    )
    return {"ok": False, "result": "Not working yet..."}


@router.get(
    path="/manage_products",
    summary="WORKS: update seller data",
    status_code=status.HTTP_200_OK,
    # response_class=ApplicationResponse[SuppliersProductsResponse],
    # FIXME:L чет падает с TypeError: __init__() takes exactly 1 positional argument (2 given)
)
async def manage_products(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[SuppliersProductsResponse]:
    # TODO: pagination?
    res = await store.orm.suppliers.get_one(
        ProductModel,
        session=session,
        where=[UserModel.id == user.schema.id],
        options=[
            joinedload(SupplierModel.products),
        ],
    )
    return {"ok": True, "result": {"supplier": res}}


@router.post(
    "/add_product/",
    summary="WORKS: Add product to database.",
    status_code=status.HTTP_200_OK,
)
async def add_product_info(
    product_data: BodyProductUploadRequest,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse:
    inserted_product = await store.orm.products.insert_one(
        session=session,
        values={
            ProductModel.supplier_id: user.schema.supplier.id,
            ProductModel.description: product_data.description,
            ProductModel.datetime: datetime.now(),
            ProductModel.name: product_data.name,
            ProductModel.category_id: product_data.category_id,
        },
    )
    if product_data.property_ids:
        await store.orm.products_property_values.insert_many(
            session=session,
            values=[
                {
                    ProductPropertyValueModel.product_id: inserted_product.id,
                    ProductPropertyValueModel.property_value_id: property_value_id,
                }
                for property_value_id in product_data.property_ids
            ],
        )
    if product_data.varitaion_ids:
        await store.orm.products_variation_values.insert_many(
            session=session,
            values=[
                {
                    ProductVariationValueModel.product_id: inserted_product.id,
                    ProductVariationValueModel.variation_value_id: variation_value_id,
                }
                for variation_value_id in product_data.varitaion_ids
            ],
        )

    await store.orm.products_prices.insert_many(
        session=session,
        values=[
            {
                ProductPriceModel.product_id: inserted_product.id,
                ProductPriceModel.discount: price.discount,
                ProductPriceModel.value: price.value,
                ProductPriceModel.min_quantity: price.min_quantity,
                ProductPriceModel.start_date: price.start_date,
                ProductPriceModel.end_date: price.end_date,
            }
            for price in product_data.prices
        ],
    )
    return ApplicationResponse(ok=True)


@router.get(
    "/company_info/",
    summary="WORKS: Get company info (name, logo_url) by token.",
    status_code=status.HTTP_200_OK,
)
async def get_supplier_company_info(
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
):
    company = await store.orm.companies.get_one(
        session=session, where=[CompanyModel.supplier_id == user.schema.supplier.id]
    )
    return ApplicationResponse(ok=True, result=company)
