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


@suppliers.get("/get_product_properties/",
    summary="WORKS (ex. 11): Get all property names by category_id.",
    response_model=ResultListOut)
async def get_product_properties_from_db(category_id: int,
                                session: AsyncSession = Depends(get_session)):
    is_category_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_ID_IS_NOT_EXIST"
        )
    properties = await session\
        .execute(text(QUERY_TO_GET_PROPERTIES.format(category_id=category_id)))
    if not properties:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PROPERTIES_NOT_FOUND"
        )
    properties = [dict(row) for row in properties]
    json_properties = dict()
    for row in properties:
        if row['name'] not in json_properties:
            json_properties[row['name']] = list()
        json_properties[row['name']].append(row['value'])
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": json_properties}
    )
    

@suppliers.get("/get_product_variations/",
    summary="WORKS (example 11): Get all variation names and values by category_id.",
    response_model=ResultListOut)
async def get_product_variations_from_db(category_id: int,
                                         session: AsyncSession = Depends(get_session)):
    is_category_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_ID_IS_NOT_EXIST"
        )
    variations = await session\
        .execute(text(QUERY_TO_GET_VARIATIONS.format(category_id=category_id)))
    if not variations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VARIATIONS_NOT_FOUND"
        )
    variations = [dict(row) for row in variations]
    json_variations = dict()
    for row in variations:
        if row['name'] not in json_variations:
            json_variations[row['name']] = list()
        json_variations[row['name']].append(row['value'])

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": json_variations}
    )


@suppliers.post("/add_product/",
    summary="WORKS: Add product to database.",
    response_model=ProductIdOut)
async def add_product_info_to_db(product_info: ProductInfo,
                            properties: List[PropertiesDict],
                            variations: List[VariationsDict],
                            prices: List[ProductPrices],
                            Authorize: AuthJWT = Depends(),
                            session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PRODUCT_PRICES_IS_EMPTY"
        )
    user_id = await User.get_user_id(email=user_email)
    supplier_id = await Supplier.get_supplier_id(user_id=user_id)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_SUPPLIER"
        )
    category_id = product_info.category_id
    is_category_id_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_id_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_ID_IS_NOT_EXIST"
        )
    current_datetime = utils.get_moscow_datetime()
    product = Product(
        supplier_id=supplier_id,
        category_id=category_id,
        name=product_info.product_name,
        description=product_info.description,
        datetime=current_datetime,
        UUID=''
    )
    session.add(product)
    await session.commit()
    product_id = await session\
                .execute(select(func.max(Product.id))\
                .where(and_(Product.supplier_id.__eq__(supplier_id),
                            Product.name.__eq__(product_info.product_name))))
    product_id = product_id.scalar()

    for property in properties:
        category_property_type_id = await session\
            .execute(select(CategoryPropertyType.id)\
            .where(CategoryPropertyType.name.__eq__(property.name)))
        category_property_type_id = category_property_type_id.scalar()
        if not category_property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PROPERTY_NOT_FOUND", name=property.name)
            )
        is_property_match_category = await session\
            .execute(select(CategoryProperty.id)\
            .where(and_(CategoryProperty.category_id.__eq__(category_id),
                        CategoryProperty.property_type_id.__eq__(category_property_type_id))))
        is_property_match_category = bool(is_property_match_category.scalar())
        if not is_property_match_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PROPERTY_IS_NOT_MATCH_CATEGORY", name=property.name)
            )
        category_property_value_id = await CategoryPropertyValue.get_category_property_value_id(
                                            category_property_type_id=category_property_type_id,
                                            value=property.value,
                                            optional_value=property.optional_value)            
        if not category_property_value_id:
            category_property_value = CategoryPropertyValue(
                property_type_id=category_property_type_id,
                value=property.value,
                optional_value=property.optional_value
            )
            session.add(category_property_value)
            await session.commit()
            category_property_value_id = await CategoryPropertyValue.get_category_property_value_id(
                                                category_property_type_id=category_property_type_id,
                                                value=property.value,
                                                optional_value=property.optional_value) 
        product_property_value = ProductPropertyValue(
            product_id=product_id,
            property_value_id=category_property_value_id
        )
        session.add(product_property_value)
    
    for variation in variations:
        category_variation_type_id = await session\
            .execute(select(CategoryVariation.variation_type_id)\
            .join(CategoryVariationType)\
            .where(and_(CategoryVariationType.name.__eq__(variation.name),
                        CategoryVariation.category_id.__eq__(category_id))))
        category_variation_type_id = category_variation_type_id.scalar()
        if not category_variation_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="VARIATION_NAME_IS_NOT_EXIST", name=variation.name)
            )
        category_variation_value_id = await CategoryVariationValue.get_category_variation_value_id(
                                                    category_variation_type_id=category_variation_type_id,
                                                    value=variation.value)
        if not category_variation_value_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="VARIATION_VALUE_IS_NOT_EXIST", value=variation.value)
            )
        product_variation_value_id_parent = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
        if not product_variation_value_id_parent:
            product_variation_value = ProductVariationValue(
                product_id=product_id,
                variation_value_id=category_variation_value_id
            )
            session.add(product_variation_value)
            await session.commit()
            product_variation_value_id_parent = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
        if not variation.childs:
            product_variations_count = ProductVariationCount(
                product_variation_value1_id=product_variation_value_id_parent,
                count=variation.count
            )
            session.add(product_variations_count)
        else:
            for child_variation in variation.childs:
                category_variation_type_id = await session\
                    .execute(select(CategoryVariation.variation_type_id)\
                    .join(CategoryVariationType)\
                    .where(and_(CategoryVariationType.name.__eq__(child_variation.name),
                                CategoryVariation.category_id.__eq__(category_id))))
                category_variation_type_id = category_variation_type_id.scalar()
                if not category_variation_type_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=dict(error="VARIATION_NAME_IS_NOT_EXIST", name=child_variation.name)
                    )
                category_variation_value_id = await CategoryVariationValue.get_category_variation_value_id(
                                                    category_variation_type_id=category_variation_type_id,
                                                    value=child_variation.value)
                if not category_variation_value_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=dict(error="VARIATION_VALUE_IS_NOT_EXIST", value=child_variation.value)
                    )
                product_variation_value_id_child = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
                if not product_variation_value_id_child:
                    product_variation_value = ProductVariationValue(
                        product_id=product_id,
                        variation_value_id=category_variation_value_id
                    )
                    session.add(product_variation_value)
                    await session.commit()
                    product_variation_value_id_child = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
                product_variations_count = ProductVariationCount(
                    product_variation_value1_id=product_variation_value_id_parent,
                    product_variation_value2_id=product_variation_value_id_child,
                    count=child_variation.count
                )
                session.add(product_variations_count)

    for price in prices:
        product_price = ProductPrice(
            product_id=product_id,
            value=price.value,
            min_quantity=price.quantity
        )
        session.add(product_price)
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"product_id": product_id}
    )
