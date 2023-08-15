from typing import List, Optional

from corecrud import (
    Join,
    Limit,
    Offset,
    Options,
    OrderBy,
    Returning,
    SelectFrom,
    Values,
    Where,
)
from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, selectinload
from starlette import status

from core.app import aws_s3, crud
from core.depends import DatabaseSession, Image, SupplierAuthorization, supplier
from core.settings import aws_s3_settings
from orm import (
    CategoryPropertyModel,
    CategoryPropertyValueModel,
    CategoryVariationModel,
    CategoryVariationTypeModel,
    CategoryVariationValueModel,
    CompanyImageModel,
    CompanyModel,
    CompanyPhoneModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationValueModel,
    SupplierModel,
    SupplierNotificationsModel,
    UserModel,
)
from schemas import (
    ApplicationResponse,
    CategoryPropertyValue,
    CategoryVariationValue,
    CompanyImage,
    Product,
    ProductImage,
    Supplier,
    SupplierNotifications,
)
from schemas.uploads import (
    CompanyDataUpdateUpload,
    CompanyPhoneDataUpdateUpload,
    PaginationUpload,
    ProductEditUpload,
    ProductUpload,
    SortFilterProductsUpload,
    SupplierDataUpdateUpload,
    SupplierNotificationsUpdateUpload,
)
from typing_ import RouteReturnT

router = APIRouter(dependencies=[Depends(supplier)])


@router.get(
    path="/getSupplierInfo",
    deprecated=True,
    description="Moved to /login/current/",
    summary="WORKS: Get supplier info (personal and business).",
    response_model=ApplicationResponse[Supplier],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_supplier_data_info(user: SupplierAuthorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.supplier,
    }


async def get_product_properties_core(
    session: AsyncSession, category_id: int
) -> List[CategoryPropertyValue]:
    return await crud.categories_property_values.select.many(
        Where(CategoryPropertyModel.category_id == category_id),
        SelectFrom(
            join(
                CategoryPropertyValueModel,
                CategoryPropertyModel,
                CategoryPropertyValueModel.property_type_id
                == CategoryPropertyModel.property_type_id,
            )
        ),
        session=session,
    )


@router.get(
    path="/getCategoryProperties/{category_id}",
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryPropertyValue]],
    status_code=status.HTTP_200_OK,
)
async def get_product_properties(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_properties_core(session=session, category_id=category_id),
    }


async def get_product_variations_core(
    session: AsyncSession, category_id: int
) -> List[CategoryVariationValue]:
    return await crud.categories_variation_values.select.many(
        Where(CategoryVariationModel.category_id == category_id),
        Options(
            selectinload(CategoryVariationValueModel.type),
        ),
        SelectFrom(
            join(
                CategoryVariationModel,
                CategoryVariationTypeModel,
                CategoryVariationModel.variation_type_id == CategoryVariationTypeModel.id,
            )
        ),
        session=session,
    )


@router.get(
    path="/getCategoryVariations/{category_id}",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryVariationValue]],
    status_code=status.HTTP_200_OK,
)
async def get_product_variations(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_variations_core(session=session, category_id=category_id),
    }


async def add_product_info_core(
    request: ProductUpload,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await crud.products.insert.one(
        Values(
            {
                ProductModel.supplier_id: supplier_id,
                ProductModel.description: request.description,
                ProductModel.name: request.name,
                ProductModel.category_id: request.category_id,
            }
        ),
        Returning(ProductModel),
        session=session,
    )
    if request.properties:
        await crud.products_property_values.insert.many(
            Values(
                [
                    {
                        ProductPropertyValueModel.product_id: product.id,
                        ProductPropertyValueModel.property_value_id: property_value_id,
                    }
                    for property_value_id in request.properties
                ]
            ),
            Returning(ProductPropertyValueModel.id),
            session=session,
        )
    if request.variations:
        await crud.products_variation_values.insert.many(
            Values(
                [
                    {
                        ProductVariationValueModel.product_id: product.id,
                        ProductVariationValueModel.variation_value_id: variation_value_id,
                    }
                    for variation_value_id in request.variations
                ]
            ),
            Returning(ProductVariationValueModel.id),
            session=session,
        )

    await crud.products_prices.insert.many(
        Values(
            [
                {
                    ProductPriceModel.product_id: product.id,
                }
                | price.dict()
                for price in request.prices
            ],
        ),
        Returning(ProductPriceModel.id),
        session=session,
    )

    return product


@router.post(
    path="/addProduct",
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def add_product_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    request: ProductUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_product_info_core(
            request=request, supplier_id=user.supplier.id, session=session
        ),
    }


async def edit_product_info_core(
    request: ProductEditUpload,
    product_id: int,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await crud.products.update.one(
        Where(
            ProductModel.id == product_id,
            ProductModel.supplier_id == supplier_id,
        ),
        Values(
            {
                ProductModel.name: request.name,
                ProductModel.description: request.description,
                ProductModel.category_id: request.category_id,
            }
        ),
        Returning(ProductModel),
        session=session,
    )
    if request.properties:
        await crud.products_property_values.insert.many(
            Values(
                [
                    {
                        ProductPropertyValueModel.product_id: product.id,
                        ProductPropertyValueModel.property_value_id: property_value_id,
                    }
                    for property_value_id in request.properties
                ]
            ),
            Returning(ProductPropertyValueModel.id),
            session=session,
        )
    if request.variations:
        await crud.products_variation_values.insert.many(
            Values(
                [
                    {
                        ProductVariationValueModel.product_id: product.id,
                        ProductVariationValueModel.variation_value_id: variation_value_id,
                    }
                    for variation_value_id in request.variations
                ]
            ),
            Returning(ProductVariationValueModel.id),
            session=session,
        )

    if request.prices:
        await crud.products_prices.insert.many(
            Values(
                [
                    {
                        ProductPriceModel.product_id: product.id,
                    }
                    | price.dict()
                    for price in request.prices
                ],
            ),
            Returning(ProductPriceModel.id),
            session=session,
        )

    return product


@router.put(
    path="/editProduct/{product_id}",
    summary="WORKS: Edit product",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def edit_product_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Path(...),
    request: ProductEditUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await edit_product_info_core(
            request=request, product_id=product_id, supplier_id=user.supplier.id, session=session
        ),
    }


async def restore_products_core(
    session: AsyncSession, supplier_id: int, products: List[int]
) -> None:
    await crud.products.update.many(
        Where(and_(ProductModel.id.in_(products), ProductModel.supplier_id == supplier_id)),
        Values(
            {
                ProductModel.is_active: True,
            }
        ),
        Returning(ProductModel.id),
        session=session,
    )


@router.post(
    path="/restoreProducts",
    summary="WORKS: Restore products (change is_active to True).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def restore_products(
    user: SupplierAuthorization,
    session: DatabaseSession,
    products: List[int] = Body(...),
) -> RouteReturnT:
    await restore_products_core(
        session=session,
        supplier_id=user.supplier.id,
        products=products,
    )

    return {
        "ok": True,
        "result": True,
    }


async def manage_products_core(
    session: AsyncSession,
    supplier_id: int,
    offset: int,
    limit: int,
    filters: SortFilterProductsUpload,
) -> List[ProductModel]:
    return await crud.products.select.many(
        Where(
            ProductModel.supplier_id == supplier_id,
            ProductModel.category_id.in_(filters.category_ids) if filters.category_ids else True,
            ProductModel.is_active == filters.is_active if filters.is_active is not None else True,
            (ProductPriceModel.discount > 0)
            if filters.on_sale
            else (ProductPriceModel.discount == 0)
            if filters.on_sale is False
            else True,
        ),
        Join(ProductPriceModel, ProductPriceModel.product_id == ProductModel.id),
        Options(
            selectinload(ProductModel.prices),
            selectinload(ProductModel.supplier).joinedload(SupplierModel.company),
            selectinload(ProductModel.category),
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(filters.sort.by.asc() if filters.ascending else filters.sort.by.desc()),
        session=session,
    )


@router.post(
    path="/products",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def products(
    user: SupplierAuthorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    filters: SortFilterProductsUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await manage_products_core(
            session=session,
            supplier_id=user.supplier.id,
            offset=pagination.offset,
            limit=pagination.limit,
            filters=filters,
        ),
    }


async def delete_products_core(
    session: AsyncSession, supplier_id: int, products: List[int]
) -> None:
    await crud.products.update.many(
        Where(and_(ProductModel.id.in_(products), ProductModel.supplier_id == supplier_id)),
        Values(
            {
                ProductModel.is_active: False,
            }
        ),
        Returning(ProductModel.id),
        session=session,
    )


@router.post(
    path="/deleteProducts",
    summary="WORKS: Delete products (change is_active to False).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_products(
    user: SupplierAuthorization,
    session: DatabaseSession,
    products: List[int] = Body(...),
) -> RouteReturnT:
    await delete_products_core(
        session=session,
        supplier_id=user.supplier.id,
        products=products,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/uploadProductImage",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_200_OK,
)
async def upload_product_image(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
    order: int = Query(...),
) -> RouteReturnT:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    product = await crud.products.select.one(
        Where(
            and_(ProductModel.id == product_id, ProductModel.supplier_id == user.supplier.id),
        ),
        session=session,
    )
    if not product:
        raise HTTPException(
            detail="Product not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    product_image = await crud.products_images.select.one(
        Where(
            and_(
                ProductImageModel.product_id == product_id,
                ProductImageModel.order == order,
            )
        ),
        session=session,
    )
    if product_image:
        raise HTTPException(
            detail="Try another order",
            status_code=status.HTTP_409_CONFLICT,
        )

    product_image = await crud.products_images.insert.one(
        Values(
            {
                ProductImageModel.image_url: link,
                ProductImageModel.product_id: product_id,
                ProductImageModel.order: order,
            }
        ),
        Returning(ProductImageModel),
        session=session,
    )

    return {
        "ok": True,
        "result": product_image,
    }


@router.delete(
    path="/deleteProductImage",
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_product_image(
    session: DatabaseSession,
    product_id: int = Query(...),
    order: int = Query(...),
) -> RouteReturnT:
    image = await crud.products_images.delete.many(
        Where(
            and_(
                ProductImageModel.product_id == product_id,
                ProductImageModel.order == order,
            ),
        ),
        Returning(ProductImageModel),
        session=session,
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image.image_url,
    )

    return {
        "ok": True,
        "result": True,
    }


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
    path="/businessInfo/update",
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
    path="/businessInfo",
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


@router.get(
    path="/companyLogo",
    summary="WORKS: returns company logo",
    response_model=ApplicationResponse[str],
    status_code=status.HTTP_200_OK,
)
async def get_company_logo(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.supplier.company.logo_url,
    }


async def update_company_logo_core(
    session: DatabaseSession,
    company_id: int,
    file: UploadFile,
) -> str:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_COMPANY_IMAGES_BUCKET, file=file
    )

    return await crud.companies.update.one(
        Values(
            {CompanyModel.logo_url: link},
        ),
        Where(CompanyModel.id == company_id),
        Returning(CompanyModel.logo_url),
        session=session,
    )


@router.post(
    path="/companyLogo/update",
    summary="WORKS: Uploads company logo",
    response_model=ApplicationResponse[str],
    status_code=status.HTTP_200_OK,
)
async def update_company_logo(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await update_company_logo_core(
            session=session,
            company_id=user.supplier.company.id,
            file=file,
        ),
    }


async def upload_company_image_core(
    session: AsyncSession,
    company_id: int,
    file: UploadFile,
) -> CompanyImageModel:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    return await crud.companies_images.insert.one(
        Values(
            {
                CompanyImageModel.company_id: company_id,
                CompanyImageModel.url: link,
            },
        ),
        Returning(CompanyImageModel),
        session=session,
    )


@router.post(
    path="/uploadCompanyImage",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_200_OK,
)
async def upload_company_image(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await upload_company_image_core(
            session=session,
            company_id=user.supplier.company.id,
            file=file,
        ),
    }


@router.delete(
    path="/deleteCompanyImage",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_company_image(
    user: SupplierAuthorization,
    session: DatabaseSession,
    company_image_id: int = Query(...),
) -> RouteReturnT:
    image = await crud.companies_images.delete.one(
        Where(
            and_(
                CompanyImageModel.id == company_image_id,
                CompanyImageModel.company_id == user.supplier.company.id,
            ),
        ),
        Returning(CompanyImageModel.url),
        session=session,
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image,
    )

    return {
        "ok": True,
        "result": True,
    }


async def update_notifications_core(
    session: AsyncSession,
    supplier_id: int,
    notification_data_request: Optional[SupplierNotificationsUpdateUpload],
) -> None:
    if notification_data_request:
        await crud.suppliers_notifications.update.one(
            Values(notification_data_request.dict()),
            Where(SupplierNotificationsModel.supplier_id == supplier_id),
            Returning(SupplierNotificationsModel.id),
            session=session,
        )


@router.post(
    path="/notifications/update",
    summary="WORKS: update notifications for supplier",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def update_notifications(
    user: SupplierAuthorization,
    session: DatabaseSession,
    notification_data_request: Optional[SupplierNotificationsUpdateUpload] = Body(None),
) -> RouteReturnT:
    await update_notifications_core(
        session=session,
        supplier_id=user.supplier.id,
        notification_data_request=notification_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_notifications_core(
    session: AsyncSession,
    supplier_id: int,
) -> SupplierNotificationsModel:
    return await crud.suppliers_notifications.select.one(
        Where(SupplierNotificationsModel.supplier_id == supplier_id),
        session=session,
    )


@router.get(
    "/notifications",
    summary="WORKS: get supplier notifications",
    response_model=ApplicationResponse[SupplierNotifications],
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_notifications_core(session=session, supplier_id=user.supplier.id),
    }


@router.get(
    path="/hasBusinessInfo",
    summary="WORKS: get Company info",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
def has_business_info(user: SupplierAuthorization) -> RouteReturnT:
    return {"ok": True, "result": bool(user.supplier.company)}


@router.get(
    path="/hasPersonalInfo",
    summary="WORKS: get Personal info",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
def has_personal_info(user: SupplierAuthorization) -> RouteReturnT:
    return {"ok": True, "result": bool(user.first_name)}
