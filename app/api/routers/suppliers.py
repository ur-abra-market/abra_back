# mypy: disable-error-code="arg-type,return-value,no-any-return"

from datetime import datetime
from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.aws_s3 import aws_s3
from core.depends import (
    FileObjects,
    UserObjects,
    auth_required,
    get_session,
    image_required,
)
from core.orm import orm
from core.settings import aws_s3_settings
from orm import (
    CategoryPropertyModel,
    CategoryPropertyValueModel,
    CategoryVariationModel,
    CategoryVariationTypeModel,
    CategoryVariationValueModel,
    CompanyImageModel,
    CompanyModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationValueModel,
    SupplierModel,
    UserModel,
)
from schemas import (
    ApplicationResponse,
    BodyCompanyDataRequest,
    BodyProductUploadRequest,
    BodySupplierDataRequest,
    BodyUserDataRequest,
    CategoryPropertyValue,
    CategoryVariationValue,
    Company,
    CompanyImage,
    Product,
    ProductImage,
    QueryPaginationRequest,
    Supplier,
)


async def supplier_required(user: UserObjects = Depends(auth_required)) -> None:
    if not user.orm.supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )


router = APIRouter(dependencies=[Depends(supplier_required)])


async def get_supplier_data_info_core(supplier_id: int, session: AsyncSession) -> SupplierModel:
    return await orm.suppliers.get_one_by(
        session=session,
        id=supplier_id,
        options=[joinedload(SupplierModel.company), joinedload(SupplierModel.addresses)],
    )


@router.get(
    path="/getSupplierInfo/",
    summary="WORKS: Get supplier info (personal and business).",
    response_model=ApplicationResponse[Supplier],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_supplier_info/",
    description="Moved to /suppliers/getSupplierInfo",
    deprecated=True,
    summary="WORKS: Get supplier info (personal and business).",
    response_model=ApplicationResponse[Supplier],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_supplier_data_info(
    user: UserObjects = Depends(auth_required), session: AsyncSession = Depends(get_session)
) -> ApplicationResponse[Supplier]:
    return {
        "ok": True,
        "result": await get_supplier_data_info_core(
            supplier_id=user.schema.supplier.id, session=session
        ),
    }


async def send_account_info_core(
    session: AsyncSession,
    user_id: int,
    supplier_id: int,
    user_data_request: BodyUserDataRequest,
    supplier_data_request: BodySupplierDataRequest,
    company_data_request: BodyCompanyDataRequest,
) -> None:
    await orm.users.update_one(
        session=session, values=user_data_request.dict(), where=UserModel.id == user_id
    )
    await orm.suppliers.update_one(
        session=session, values=supplier_data_request.dict(), where=SupplierModel.id == supplier_id
    )
    await orm.companies.update_one(
        session=session,
        values=company_data_request.dict(),
        where=CompanyModel.supplier_id == supplier_id,
    )


@router.post(
    path="/sendAccountInfo/",
    summary="WORKS: Should be discussed. 'images_url' insert images in company_images, other parameters update corresponding values.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/send_account_info/",
    description="Moved to /suppliers/sendAccountInfo",
    deprecated=True,
    summary="WORKS: Should be discussed. 'images_url' insert images in company_images, other parameters update corresponding values.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def send_account_info(
    user_data_request: BodyUserDataRequest = Body(...),
    supplier_data_request: BodySupplierDataRequest = Body(...),
    company_data_request: BodyCompanyDataRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await send_account_info_core(
        session=session,
        user_id=user.schema.id,
        supplier_id=user.schema.supplier.id,
        user_data_request=user_data_request,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_product_properties_core(
    session: AsyncSession, category_id: int
) -> List[CategoryPropertyValue]:
    return await orm.categories_property_values.get_many_unique(
        session=session,
        where=[CategoryPropertyModel.category_id == category_id],
        select_from=[
            join(
                CategoryPropertyValueModel,
                CategoryPropertyModel,
                CategoryPropertyValueModel.property_type_id
                == CategoryPropertyModel.property_type_id,
            )
        ],
    )


@router.get(
    path="/getCategoryProperties/{category_id}/",
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryPropertyValue]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_category_properties/{category_id}/",
    description="Moved to /suppliers/getCategoryProperties/{category_id}",
    deprecated=True,
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryPropertyValue]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_product_properties(
    category_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[CategoryPropertyValue]]:
    return {
        "ok": True,
        "result": await get_product_properties_core(session=session, category_id=category_id),
    }


async def get_product_variations_core(
    session: AsyncSession, category_id: int
) -> List[CategoryVariationValue]:
    return await orm.categories_variation_values.get_many_unique(
        session=session,
        where=[CategoryVariationModel.category_id == category_id],
        select_from=[
            join(
                CategoryVariationModel,
                CategoryVariationTypeModel,
                CategoryVariationModel.variation_type_id == CategoryVariationTypeModel.id,
            )
        ],
        options=[
            joinedload(CategoryVariationValueModel.type),
        ],
    )


@router.get(
    path="/getCategoryVariations/{category_id}/",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryVariationValue]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_category_variations/{category_id}/",
    description="Moved to /suppliers/getCategoryVariations/{category_id}",
    deprecated=True,
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryVariationValue]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_product_variations(
    category_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[CategoryVariationValue]]:
    return {
        "ok": True,
        "result": await get_product_variations_core(session=session, category_id=category_id),
    }


async def add_product_info_core(
    request: BodyProductUploadRequest,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await orm.products.insert_one(
        session=session,
        values={
            ProductModel.supplier_id: supplier_id,
            ProductModel.description: request.description,
            ProductModel.datetime: datetime.now(),
            ProductModel.name: request.name,
            ProductModel.category_id: request.category_id,
        },
    )
    if request.property_ids:
        await orm.products_property_values.insert_many(
            session=session,
            values=[
                {
                    ProductPropertyValueModel.product_id: product.id,
                    ProductPropertyValueModel.property_value_id: property_value_id,
                }
                for property_value_id in request.property_ids
            ],
        )
    if request.varitaion_ids:
        await orm.products_variation_values.insert_many(
            session=session,
            values=[
                {
                    ProductVariationValueModel.product_id: product.id,
                    ProductVariationValueModel.variation_value_id: variation_value_id,
                }
                for variation_value_id in request.varitaion_ids
            ],
        )

    await orm.products_prices.insert_many(
        session=session,
        values=[
            {
                ProductPriceModel.product_id: product.id,
                ProductPriceModel.discount: price.discount,
                ProductPriceModel.value: price.value,
                ProductPriceModel.min_quantity: price.min_quantity,
                ProductPriceModel.start_date: price.start_date,
                ProductPriceModel.end_date: price.end_date,
            }
            for price in request.prices
        ],
    )

    return product


@router.post(
    path="/addProduct/",
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/add_product/",
    description="Moved to /suppliers/addProduct",
    deprecated=True,
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def add_product_info(
    request: BodyProductUploadRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[Product]:
    product = await add_product_info_core(
        request=request, supplier_id=user.schema.supplier.id, session=session
    )

    return {
        "ok": True,
        "result": product,
    }


async def manage_products_core(
    session: AsyncSession,
    supplier_id: int,
    offset: int,
    limit: int,
) -> List[ProductModel]:
    return await orm.products.get_many_by(
        session=session,
        supplier_id=supplier_id,
        options=[joinedload(ProductModel.prices)],
        offset=offset,
        limit=limit,
    )


@router.get(
    path="/manageProducts/",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/manage_products/",
    description="Moved to /suppliers/manageProducts",
    deprecated=True,
    summary="WORKS: Get list of all suppliers products.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def manage_products(
    pagination: QueryPaginationRequest = Depends(),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Product]]:
    return {
        "ok": True,
        "result": await manage_products_core(
            session=session,
            supplier_id=user.schema.supplier.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def delete_products_core(
    session: AsyncSession, supplier_id: int, products: List[int]
) -> None:
    await orm.products.update_many(
        session=session,
        values={
            ProductModel.is_active: 0,
        },
        where=and_(ProductModel.id.in_(products), ProductModel.supplier_id == supplier_id),
    )


@router.patch(
    path="/deleteProducts/",
    summary="WORKS: Delete products (change is_active to 0).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.patch(
    path="/delete_products/",
    description="Moved to /suppliers/deleteProducts",
    deprecated=True,
    summary="WORKS: Delete products (change is_active to 0).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def delete_products(
    products: List[int] = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    await delete_products_core(
        session=session,
        supplier_id=user.schema.supplier.id,
        products=products,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/uploadProductImage/",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/upload_product_image/",
    description="Moved to /suppliers/uploadProductImage",
    deprecated=True,
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def upload_product_image(
    file: FileObjects = Depends(image_required),
    product_id: int = Query(...),
    order: int = Query(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[ProductImage]:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    product_image = await orm.products_images.insert_one(
        session=session,
        values={
            ProductImageModel.image_url: link,
            ProductImageModel.product_id: product_id,
            ProductImageModel.serial_number: order,
        },
    )

    return {"ok": True, "result": product_image}


@router.delete(
    path="/deleteProductImage/",
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/delete_product_image/",
    description="Moved to /suppliers/uploadProductImage",
    deprecated=True,
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def delete_product_image(
    product_id: int = Query(...),
    serial_number: int = Query(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    image = await orm.products_images.delete_one(
        session=session,
        where=and_(
            ProductImageModel.product_id == product_id,
            ProductImageModel.serial_number == serial_number,
        ),
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image.image_url,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_supplier_company_info_core(session: AsyncSession, supplier_id: int) -> CompanyModel:
    return await orm.companies.get_one_by(session=session, supplier_id=supplier_id)


@router.get(
    path="/companyInfo/",
    summary="WORKS: Get company info (name, logo_url) by token.",
    response_model=ApplicationResponse[Company],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/company_info/",
    description="Moved to /suppliers/companyInfo",
    deprecated=True,
    summary="WORKS: Get company info (name, logo_url) by token.",
    response_model=ApplicationResponse[Company],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_supplier_company_info(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[Company]:
    return {
        "ok": True,
        "result": await get_supplier_company_info_core(
            session=session, supplier_id=user.schema.supplier.id
        ),
    }


@router.post(
    path="/uploadCompanyImage/",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/upload_company_image/",
    description="Moved to /suppliers/uploadCompanyImage",
    deprecated=True,
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def upload_company_image(
    file: FileObjects = Depends(image_required),
    order: int = Query(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[CompanyImage]:
    company = await orm.companies.get_one_by(
        session=session,
        supplier_id=user.schema.supplier.id,
    )

    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    company_image = await orm.companies_images.insert_one(
        session=session,
        values={
            CompanyImageModel.company_id: company.id,
            CompanyImageModel.url: link,
            CompanyImageModel.order: order,
        },
    )

    return {
        "ok": True,
        "result": company_image,
    }


@router.delete(
    path="/deleteCompanyImage/",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.delete(
    path="/delete_company_image/",
    description="Moved to /suppliers/deleteCompanyImage",
    deprecated=True,
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def delete_company_image(
    order: int = Query(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    company = await orm.companies.get_one_by(
        session=session,
        supplier_id=user.schema.supplier.id,
    )
    image = await orm.companies_images.delete_one(
        session=session,
        where=and_(
            CompanyImageModel.company_id == company.id,
            CompanyImageModel.order == order,
        ),
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, url=image.url
    )

    return {
        "ok": True,
        "result": True,
    }
