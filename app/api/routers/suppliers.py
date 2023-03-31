from datetime import datetime, timezone
from pathlib import Path
import imghdr

from fastapi import APIRouter, UploadFile
from fastapi.param_functions import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, join
from sqlalchemy import and_

from starlette import status

from core.depends import UserObjects, auth_required, auth_required_supplier, get_session
from core.settings import aws_s3_settings
from core.tools import store
from orm import (
    UserModel,
    CategoryModel,
    CategoryPropertyValueModel,
    CategoryVariationValueModel,
    CategoryVariationModel,
    CategoryVariationTypeModel,
    CompanyModel,
    CompanyImageModel,
    SupplierModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationValueModel,
    ProductImageModel,
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


@router.post(
    "/upload_company_image/",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
)
async def upload_company_image(
    file: UploadFile,
    order: int,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
):

    company = await store.orm.companies.get_one(
        session=session, where=[CompanyModel.supplier_id == user.schema.supplier.id]
    )
    contents = await file.read()
    # TODO: maybe check content type instead?
    is_image = imghdr.what("", h=contents)
    if not is_image:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be an image",
        )
    await file.seek(0)
    file_extension = Path(file.filename).suffix
    link = await store.aws_s3.upload(
        bucket_name=aws_s3_settings.AWS_S3_COMPANY_IMAGES_BUCKET,
        file_data={"extension": file_extension},
        contents=contents,
        file=file,
    )

    #  TODO: try except sqlalchemy.exc.IntegrityError:
    await store.orm.companies_images.insert_one(
        session=session,
        values={
            CompanyImageModel.company_id: company.id,
            CompanyImageModel.url: link,
            CompanyImageModel.order: order,
        },
    )

    return link


@router.delete(
    "/delete_company_image/",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
)
async def delete_company_image(
    order: int,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
):
    company = await store.orm.companies.get_one(
        session=session, where=[CompanyModel.supplier_id == user.schema.supplier.id]
    )
    deleted_image = await store.orm.companies_images.delete_one(
        session=session,
        where=and_(
            CompanyImageModel.company_id == company.id,
            CompanyImageModel.order == order,
        ),
    )
    # TODO: переписать эту дичь
    key_to_delete = ["/".join(deleted_image.url.split("/")[-2:])]
    await store.aws_s3.remove(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        files_to_delete=key_to_delete,
    )


@router.delete(
    "/delete_product_image/",
    summary="NOT WORKING: Delete provided product image from AWS S3 and url from DB",
)
async def delete_product_image(
    product_image_id: int,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
):
    product_image = await store.orm.products_images.delete_one(
        session=session, where=(ProductImageModel.product_id == product_image_id,)
    )
    product_image
    # FIXME: не ищет ;(


@router.post(
    "/upload_product_image/",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
)
async def upload_product_image(
    file: UploadFile,
    product_id: int,
    order: int,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
):
    product = await store.orm.products.get_one(
        session=session, where=[ProductModel.id == product_id]
    )
    contents = await file.read()
    # TODO: maybe check content type instead?
    is_image = imghdr.what("", h=contents)
    if not is_image:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be an image",
        )
    await file.seek(0)
    file_extension = Path(file.filename).suffix
    link = await store.aws_s3.upload(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        file_data={"extension": file_extension},
        contents=contents,
        file=file,
    )
    # TODO: add unique together and handler for sql constraint error
    await store.orm.products_images.insert_one(
        session=session,
        values={
            ProductImageModel.image_url: link,
            ProductImageModel.product_id: product.id,
            ProductImageModel.order: order,
        },
    )


@router.get(
    "/get_category_variations/{category_id}/",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
)
async def get_product_variations(
    category_id: int,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
):
    # TODO: rewrite to joined query
    category = await store.orm.categories.get_one(
        session=session,
        where=[CategoryModel.id == category_id],
        options=[joinedload(CategoryModel.variations)],
    )

    var_type_ids = [var.id for var in category.variations]
    category_var_values = await store.orm.categories_variation_values.get_many_unique(
        session=session,
        where=[CategoryVariationValueModel.variation_type_id.in_(var_type_ids)],
        options=[
            joinedload(CategoryVariationValueModel.type),
        ],
    )

    category_var_values = [
        {
            "id": var.type.id,
            "type": var.type,
            "value": {"id": var.id, "name": var.value},
        }
        for var in category_var_values
    ]
    # TODO: response model
    return ApplicationResponse(ok=True, result=category_var_values)


@router.get(
    "/get_category_properties/{category_id}/",
    summary="WORKS: Get all variation names and values by category_id.",
)
async def get_product_properties(
    category_id: int,
    user: UserObjects = Depends(auth_required_supplier),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse:
    # TODO: rewrite to joined query
    category = await store.orm.categories.get_one(
        session=session,
        where=[CategoryModel.id == category_id],
        options=[joinedload(CategoryModel.properties)],
    )
    property_types_ids = [var.id for var in category.properties]
    property_values = await store.orm.categories_property_values.get_many_unique(
        session=session,
        where=[CategoryPropertyValueModel.property_type_id.in_(property_types_ids)],
    )
    # TODO: response model
    return ApplicationResponse(ok=True, result=property_values)
