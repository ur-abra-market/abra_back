from classes.response_models import *
from logic import utils
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from database import get_session
from database.models import *
import logging
from fastapi_jwt_auth import AuthJWT


suppliers = APIRouter()


@suppliers.get("/get-product-properties/",
               summary="")
async def get_product_properties(
    category_id: int,
    session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    pass


@suppliers.post("/send-account-info/",
                summary="Is not tested with JWT")
async def send_supplier_data_info(
                               supplier_info: SupplierInfo,
                               account_info: SupplierAccountInfo,
                               Authorize: AuthJWT = Depends(),
                               session: AsyncSession = Depends(get_session)) -> JSONResponse:
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user_id = await User.get_user_id(email=user_email)
    await session.execute(update(Supplier)\
                          .where(Supplier.user_id.__eq__(user_id))\
                          .values(license_number=supplier_info.tax_number))
    await session.commit()
    
    await session.execute(update(User)\
                          .where(User.id.__eq__(user_id))\
                          .values(first_name=supplier_info.first_name,
                                  last_name=supplier_info.last_name,
                                  phone=supplier_info.phone))
    await session.commit()

    supplier_data: UserAdress = UserAdress(user_id=user_id,
                               country=supplier_info.country)

    supplier_id: int = await session.execute(
        select(Supplier.id)\
        .where(Supplier.user_id.__eq__(user_id))
    )
    supplier_id: int = supplier_id.scalar()
    account_data: Company = Company(
        supplier_id=supplier_id,
        name=account_info.shop_name,
        business_sector=account_info.business_sector,
        logo_url=account_info.logo_url,
        is_manufacturer=account_info.is_manufacturer,
        year_established=account_info.year_established,
        number_of_employees=account_info.number_of_emploees,
        description=account_info.description,
        photo_url=account_info.photo_url,
        phone=account_info.business_phone,
        business_email=account_info.business_email,
        address=account_info.company_address
    )
    session.add_all((supplier_data, account_data))
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "DATA_HAS_BEEN_SENT"}
    )



@suppliers.post("/add_main_product_info/",
    summary="WORKS: Add product to database. Images in [url0, url1 ...] format (optional)."
            "type_name is category name (example 'clothes')!",
    response_model=ProductIdOut)
async def add_product_info_to_db(supplier_id: int,
                            product_name: str,
                            type_name: str,
                            session: AsyncSession = Depends(get_session)):
    is_supplier_exist = await Supplier.is_supplier_exist(supplier_id=supplier_id)
    if not is_supplier_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SUPPLIER_NOT_FOUND"
        )
    # in fact, type_name is category_name
    category_id = await Category.get_category_id(category_name=type_name)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_NOT_FOUND"
        )
    current_datetime = utils.get_moscow_datetime()
    product = Product(
        supplier_id=supplier_id,
        category_id=category_id,
        name=product_name,
        datetime=current_datetime
    )
    session.add(product)
    
    product_id = await session\
                .execute(select(func.max(Product.id))\
                .where(and_(Product.supplier_id.__eq__(supplier_id),
                            Product.name.__eq__(product_name))))
    product_id = product_id.scalar()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"product_id": product_id}
    )


@suppliers.post("/add_product_images/",
    summary="WORKS: Add product images to database.",
    response_model=ProductIdOut)
async def add_product_info_to_db(product_id: int,
                            image_urls: list = list(),
                            session: AsyncSession = Depends(get_session)):
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    for serial_number, image_url in enumerate(image_urls):
        image = ProductImage(
            product_id=product_id,
            image_url=image_url,
            serial_number=serial_number
        )
        session.add(image)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "OK"}
    )


@suppliers.get("/get_product_properties/",
    summary="WORKS (example 524): "
            "Get all property names by product_id (depends on category).",
    response_model=ResultListOut)
async def get_product_properties_from_db(product_id: int,
                                         session: AsyncSession = Depends(get_session)):
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    category_id = await Product.get_category_id(product_id=product_id)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )
    property_names = await session\
        .execute(text(QUERY_TO_GET_PROPERTIES.format(category_id=category_id)))
    if not property_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PROPERTIES_NOT_FOUND"
        )
    property_names = [row[0] for row in property_names]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": property_names}
    )
    

@suppliers.post("/add_product_properties/",
    summary="WORKS: Add properties to database. "
            "Properties in {'name': 'value', ...} format. "
            "Names sctricly from /suppliers/get_product_properties/ route. "
            "Any string values.",
    response_model=ResultOut)
async def add_product_properties_to_db(product_id: int,
                                properties: dict,
                                session: AsyncSession = Depends(get_session)):
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    category_id = await Product.get_category_id(product_id=product_id)
    for name, value in properties.items():
        category_property_type_id = await session\
            .execute(select(CategoryPropertyType.id)\
            .where(CategoryPropertyType.name.__eq__(name)))
        category_property_type_id = category_property_type_id.scalar()
        if not category_property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PROPERTY_NOT_FOUND", name=name)
            )
        is_property_match_category = await session\
            .execute(select(CategoryProperty.id)\
            .where(and_(CategoryProperty.category_id.__eq__(category_id),
                        CategoryProperty.property_type_id.__eq__(category_property_type_id))))
        is_property_match_category = bool(is_property_match_category.scalar())
        if not is_property_match_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PROPERTY_DOES_NOT_MATCH_CATEGORY", name=name)
            )
        category_property_value_id = await session\
            .execute(select(CategoryPropertyValue.id)\
            .where(and_(CategoryPropertyValue.property_type_id.__eq__(category_property_type_id),
                        CategoryPropertyValue.value.__eq__(value))))
        category_property_value_id = category_property_value_id.scalar()                        
        if not category_property_value_id:
            category_property_value = CategoryPropertyValue(
                property_type_id=category_property_type_id,
                value=value
            )
            session.add(category_property_value)
            category_property_value_id = await session\
                .execute(select(CategoryPropertyValue.id)\
                .where(and_(CategoryPropertyValue.property_type_id.__eq__(category_property_type_id),
                            CategoryPropertyValue.value.__eq__(value))))
            category_property_value_id = category_property_value_id.scalar()
        product_property_value = ProductPropertyValue(
            product_id=product_id,
            property_value_id=category_property_value_id
        )
        session.add(product_property_value)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "OK"}
    )


@suppliers.post("/add_product_prices/",
               summary="WORKS: Add product prices.",
               response_model=ResultOut)
async def add_product_prices_to_db(product_id: int,
                                   price_value: float,
                                   quantity_normal: int,
                                   discount: float = 0.0,
                                   quantity_discount: int = 0,
                                   session: AsyncSession = Depends(get_session)):
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    current_datetime = utils.get_moscow_datetime()
    product_price = ProductPrice(
        product_id=product_id,
        value=price_value,
        quantity=quantity_normal,
        start_date=current_datetime
    )
    session.add(product_price)
    if discount:
        product_price = ProductPrice(
            product_id=product_id,
            value=price_value,
            quantity=quantity_discount,
            discount=discount,
            start_date=current_datetime
        )
        session.add(product_price)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "OK"}
    )
    

@suppliers.get("/get_product_variations/",
    summary="WORKS (example 524): "
            "Get all variation names by product_id (depends on category).",
    response_model=ResultListOut)
async def get_product_variations_from_db(product_id: int,
                                         session: AsyncSession = Depends(get_session)):
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    category_id = await Product.get_category_id(product_id=product_id)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )
    variation_names = await session\
        .execute(text(QUERY_TO_GET_VARIATIONS.format(category_id=category_id)))
    if not variation_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VARIATIONS_NOT_FOUND"
        )
    variation_names = [row[0] for row in variation_names]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": variation_names}
    )


@suppliers.post("/add_product_variations/",
    summary="WORKS: Add variations to database. "
            "Variations in {'name1': ['value1', 'value2', ...], ...} format. "
            "Names sctricly from /suppliers/get_product_variations/ route. "
            "value1, value2 - any string values. "
            "But values always in []. Even there is only one value.",
    response_model=ResultOut)
async def add_product_variations_to_db(product_id: int,
                                variations: dict,
                                session: AsyncSession = Depends(get_session)):
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    category_id = await Product.get_category_id(product_id=product_id)
    for name, values in variations.items():
        if not isinstance(values, list):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="VALUES_MUST_BE_ARRAY"
            )
        category_variation_type_id = await session\
            .execute(select(CategoryVariationType.id)\
            .where(CategoryVariationType.name.__eq__(name)))
        category_variation_type_id = category_variation_type_id.scalar()
        if not category_variation_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="VARIATION_NOT_FOUND", name=name)
            )
        is_variation_match_category = await session\
            .execute(select(CategoryVariation.id)\
            .where(and_(CategoryVariation.category_id.__eq__(category_id),
                        CategoryVariation.variation_type_id.__eq__(category_variation_type_id))))
        is_variation_match_category = bool(is_variation_match_category.scalar())
        if not is_variation_match_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="VARIATION_DOES_NOT_MATCH_CATEGORY", name=name)
            )
        for value in values:
            category_variation_value_id = await session\
                .execute(select(CategoryVariationValue.id)\
                .where(and_(CategoryVariationValue.variation_type_id.__eq__(category_variation_type_id),
                            CategoryVariationValue.value.__eq__(value))))
            category_variation_value_id = category_variation_value_id.scalar()                        
            if not category_variation_value_id:
                category_variation_value = CategoryVariationValue(
                    variation_type_id=category_variation_type_id,
                    value=value
                )
                session.add(category_variation_value)
                category_variation_value_id = await session\
                    .execute(select(CategoryVariationValue.id)\
                    .where(and_(CategoryVariationValue.variation_type_id.__eq__(category_variation_type_id),
                                CategoryVariationValue.value.__eq__(value))))
                category_variation_value_id = category_variation_value_id.scalar()
            product_variation_value = ProductVariationValue(
                product_id=product_id,
                variation_value_id=category_variation_value_id
            )
            session.add(product_variation_value)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "OK"}
    )