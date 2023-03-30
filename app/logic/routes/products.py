import json

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import select, text, delete, insert, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
import pytz

from app.classes.response_models import (
    ResultOut,
    ProductOut,
    ListOfProducts,
)
from app.classes import response_models, request_models


from app.logic.consts import *
from app.logic import consts
from app.logic.queries import *
from app.database import get_session

from app.database.models import *
import app.database.models as models


class GradeOut(BaseModel):
    grade: dict
    grade_details: List[dict]


products = APIRouter()


@products.get(
    "/compilation/",
    summary="WORKS: Get list of products by category_id."
    " Can order by total_orders, date, price, rating.",
    response_model=response_models.ProductPaginationOut,
)
async def get_products_list_for_category(
    request_params: request_models.RequestPagination = Depends(
        request_models.ProductsCompilationRequest
    ),
    session: AsyncSession = Depends(get_session),
):
    # TODO: Maybe unite this route with POST /pagination ?
    query = (
        select(
            models.Product,
            models.ProductPrice,
        )
        .outerjoin(
            models.ProductPrice, models.ProductPrice.product_id == models.Product.id
        )
        .filter(models.Product.is_active == 1)
    )

    if request_params.category_id:
        query = query.filter(models.Product.category_id == request_params.category_id)

    product_sorting_types_map = {
        "rating": models.Product.grade_average,
        "price": models.ProductPrice.value,
        "date": models.Product.datetime,
        "total_orders": models.Product.total_orders,
    }

    if request_params.order_by:
        request_params.order_by: consts.SortingTypes
        # convert human readable sort type to field in DB
        order_by_field = product_sorting_types_map.get(
            request_params.order_by.value, None
        )

        if order_by_field and request_params.order_by.value == "date":
            query = query.order_by(desc(order_by_field))
        elif order_by_field and request_params.order_by.value != "date":
            query = query.order_by(order_by_field)

    # pagination
    if request_params.page_size and request_params.page_num:
        query = query.limit(request_params.page_size).offset(
            (request_params.page_num - 1) * request_params.page_size
        )

    raw_data = (await session.execute(query)).fetchall()
    result_output = response_models.ProductPaginationOut(total_products=0)

    # serialization
    for product_tables in raw_data:
        mapped_tables = {}
        for table in product_tables:
            # add to mapped_tables raw product data with keys:
            # 'products', 'product_prices', 'images',
            if not table:
                continue
            try:
                mapped_tables[table.__table__.name] = table.__dict__
            except AttributeError as ex:
                pass

        product_data = {
            **mapped_tables.get("products", {}),
        }
        product_prices = mapped_tables.get("product_prices", {})
        product_prices.pop("id", None)
        product_modeled = response_models.ProductOut(
            **{**product_data, **product_prices}
        )

        image_query = select(models.ProductImage).filter(
            models.ProductImage.product_id == product_modeled.id
        )
        image_data = (await session.execute(image_query)).all()
        if image_data:
            images_modeled = [
                response_models.OneImageOut(**image[0].__dict__) for image in image_data
            ]
        else:
            images_modeled = []

        all_product_data = response_models.AllProductDataOut(
            product=product_modeled, images=images_modeled
        )

        result_output.result.append(all_product_data)

    result_output.total_products = len(result_output.result)
    return result_output.dict()


@products.get(
    "/images/",
    summary="WORKS (example 1-100): Get product images by product_id.",
    response_model=response_models.ImagesOut,
)
async def get_images_for_product(product_id: int):
    images = await ProductImage.get_images(product_id=product_id)
    modeled_images = response_models.ImagesOut(
        result=[response_models.OneImageOut(**image) for image in images]
    )
    return modeled_images.dict()


@products.get(
    "/product_card/{product_id}/",
    summary="WORKS (example 1-100, 1): Get info for product card p1.",
    response_model=response_models.ProducCardOut,
)
async def get_info_for_product_card(
    product_id: int,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_optional()
    user_token = Authorize.get_jwt_subject()

    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID",
        )
    is_exist = await Product.is_product_exist(product_id=product_id)
    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCT_NOT_FOUND"
        )

    if user_token:
        user_email = json.loads(user_token)["email"]
        seller_id = await Seller.get_seller_id_by_email(email=user_email)
        is_favorite = await session.execute(
            select(SellerFavorite.id).where(
                SellerFavorite.product_id.__eq__(product_id),
                SellerFavorite.seller_id.__eq__(seller_id),
            )
        )
        is_favorite = bool(is_favorite.scalar())
    else:
        is_favorite = False

    product_with_variations_query = (
        select(
            models.Product,
            func.json_arrayagg(
                func.json_object(
                    "property_type_name",
                    models.CategoryPropertyType.name,
                    "category_varitaion_value",
                    models.CategoryVariationValue.value,
                    "category_varitaion_type_name",
                    models.CategoryVariationType.name,
                    "category_varitaion_value_id",
                    models.CategoryVariationValue.id,
                ),
                type_=JSON,
            ).label('variations'),
        )
        .outerjoin(
            models.ProductVariationValue,
            models.Product.id == models.ProductVariationValue.product_id,
        )
        .outerjoin(
            models.CategoryVariationValue,
            models.CategoryVariationValue.id
            == models.ProductVariationValue.variation_value_id,
        )
        .outerjoin(
            models.CategoryPropertyType,
            models.CategoryPropertyType.id
            == models.CategoryVariationValue.variation_type_id,
        )\
        .outerjoin(models.CategoryVariationType,
                  models.CategoryVariationType.id == models.CategoryVariationValue.variation_type_id)
        .outerjoin(
            models.ProductReview, models.ProductReview.product_id == models.Product.id
        )
        .outerjoin(models.Tags, models.Tags.product_id == models.Product.id)
        .group_by(models.Product)
        .filter(models.Product.id == product_id)
    )

    prod_with_variations = await session.execute(product_with_variations_query)
    prod_with_variations = prod_with_variations.fetchall()[0]

    # prod_with_variations == [models.Product(),
    #                    [{'property_type_name': str,
    #                      'category_varitaion_value': str,
    #                      'category_varitaion_value_id': int,
    #                      'category_varitaion_type_name': str}]]

    product, variations = prod_with_variations
    sizes = []
    colors = []
    for var in variations:
        if var.get('category_varitaion_type_name', None) == 'Color':
            colors.append({
                'value':var.get('category_varitaion_value'),
                'id':var.get('category_varitaion_value_id', None)
                })
        elif var.get('category_varitaion_type_name', None) == 'Size':
            sizes.append({
                'value':var.get('category_varitaion_value'),
                'id':var.get('category_varitaion_value_id', None)
            })

    # removing duplicates
    if sizes:
        sizes = list({v['value']:v for v in sizes}.values())
    if colors:
        colors = list({v['value']:v for v in colors}.values())

    supplier_info_modeled = {}
    supplier_info = await Supplier.get_supplier_info(product_id=product_id)
    if supplier_info:
        supplier_info_modeled = response_models.SupplierOut(**supplier_info)


    prices_query = select(models.ProductPrice).filter(
        models.ProductPrice.product_id == product_id
    )
    price_data = await session.execute(prices_query)
    price_data = price_data.all()
    prices_modeled = []
    if price_data:
        prices_modeled = [
            response_models.ProductPrice(**row[0].__dict__) for row in price_data
        ]

    grade = await Product.get_product_grade(product_id=product_id)

    product_tags_and_category_query = select(
        models.Tags.name.label('tag'),
        models.Category.name.label('category')
    )\
    .filter(models.Tags.product_id == product_id)\
    .filter(models.Category.id == product.category_id)

    tags_and_category = await session.execute(product_tags_and_category_query)
    tags_and_category = tags_and_category.all()

    tags = set()
    category_name = ''
    if tags_and_category:
        for row in tags_and_category:
            row_dict = row._mapping
            tag = row_dict.get('tag', None)
            tags.add(tag)
            category_name = row_dict.get('category', None)

    category_path = ''
    if category_name:
        category_path = await Category.get_category_path(category=category_name)

    respose_modeled = response_models.ProducCardOut(
        **{**product.__dict__,
           'sizes':sizes,
           'colors':colors,
           'prices':prices_modeled,
           'category_name':category_name,
           'category_path':category_path,
           'supplier_info':supplier_info_modeled,
           'is_favorite':is_favorite,
           'grade':grade
           }
    )
    return respose_modeled


@products.get(
    "/similar/",
    summary="WORKS (example 1-100): Get similar products by product_id.",
    response_model=ListOfProducts,
)
async def get_similar_products_in_category(
    product_id: int,
    page_num: int = 1,
    page_size: int = 6,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_optional()
    user_token = Authorize.get_jwt_subject()

    if user_token:
        user_email = json.loads(user_token)["email"]
        seller_id = await Seller.get_seller_id_by_email(email=user_email)
        is_favorite_subquery = PRODUCT_IS_FAVORITE_SUBQUERY.format(seller_id=seller_id)
    else:
        is_favorite_subquery = 0

    category_id = await Product.get_category_id(product_id=product_id)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCT_NOT_FOUND"
        )

    products_to_skip = (page_num - 1) * page_size
    products_records = await session.execute(
        text(
            QUERY_FOR_POPULAR_PRODUCTS.format(
                product_id=product_id,
                category_id=category_id,
                is_favorite_subquery=is_favorite_subquery,
                order_by="grade_average",
                page_size=page_size,
                products_to_skip=products_to_skip,
            )
        )
    )
    products_list = [dict(record) for record in products_records if products_records]
    if not products_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_PRODUCTS")

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": products_list}
    )


@products.get(
    "/popular/",
    summary="WORKS (example 1-100): Get popular products in this category.",
    response_model=ListOfProducts,
)
async def get_popular_products_in_category(
    product_id: int,
    page_num: int = 1,
    page_size: int = 6,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_optional()
    user_token = Authorize.get_jwt_subject()

    if user_token:
        user_email = json.loads(user_token)["email"]
        seller_id = await Seller.get_seller_id_by_email(email=user_email)
        is_favorite_subquery = PRODUCT_IS_FAVORITE_SUBQUERY.format(seller_id=seller_id)
    else:
        is_favorite_subquery = 0

    category_id = await Product.get_category_id(product_id=product_id)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCT_NOT_FOUND"
        )

    products_to_skip = (page_num - 1) * page_size
    products_records = await session.execute(
        text(
            QUERY_FOR_POPULAR_PRODUCTS.format(
                product_id=product_id,
                category_id=category_id,
                is_favorite_subquery=is_favorite_subquery,
                order_by="p.total_orders",
                page_size=page_size,
                products_to_skip=products_to_skip,
            )
        )
    )
    products_list = [dict(record) for record in products_records if products_records]
    if not products_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_PRODUCTS")

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": products_list}
    )


@products.post(
    "/pagination/",
    summary="WORKS: Pagination for products list page (sort_type = rating/price/date).",
    response_model=response_models.ProductPaginationOut,
)
async def pagination(
    data: request_models.ProductsPaginationRequest,
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(
            models.Product,
            models.ProductPrice,
            models.ProductPropertyValue,
            models.CategoryPropertyValue,
            models.ProductVariationValue,
            models.CategoryVariationValue,
            models.Supplier,
            models.User,
        )
        .outerjoin(
            models.ProductPropertyValue,
            models.ProductPropertyValue.product_id == models.Product.id,
        )
        .outerjoin(
            models.CategoryPropertyValue,
            models.CategoryPropertyValue.id
            == models.ProductPropertyValue.property_value_id,
        )
        .outerjoin(
            models.ProductPrice, models.ProductPrice.product_id == models.Product.id
        )
        .outerjoin(models.Supplier, Product.supplier_id == models.Supplier.id)
        .outerjoin(models.User, models.Supplier.user_id == models.User.id)
        .outerjoin(
            models.ProductVariationValue,
            models.ProductVariationValue.product_id == models.Product.id,
        )
        .outerjoin(
            models.CategoryVariationValue,
            models.ProductVariationValue.variation_value_id
            == models.CategoryVariationValue.id,
        )
        .filter(models.Product.is_active == 1)
    )

    if data.category_id:
        query = query.filter(models.Category.id == data.category_id)

    if data.sizes:
        # TODO: refactor and join the main query
        size_variation_type_id = await CategoryVariationType.get_id(name="size")
        query = query.filter(
            models.CategoryVariationValue.variation_type_id == size_variation_type_id,
            models.CategoryVariationValue.value.in_(data.sizes),
        )

    now = datetime.now(tz=pytz.timezone("Europe/Moscow")).replace(tzinfo=None)

    query = query.filter(models.ProductPrice.start_date < now).filter(
        func.coalesce(models.ProductPrice.end_date, datetime(year=2099, month=1, day=1))
        > now
    )

    if data.bottom_price is not None:
        query = query.filter(models.ProductPrice.value >= data.bottom_price)
    if data.top_price is not None:
        query = query.filter(models.ProductPrice.value <= data.bottom_price)
    if data.with_discount:
        query = query.filter(func.coalesce(models.ProductPrice.discount, 0) > 0)

    if data.materials:
        query = query.filter(models.CategoryPropertyValue.value.in_(data.materials))

    if data.ascending:
        query = query.order_by(
            models.Product.grade_average,
            models.ProductPrice.value,
            models.Product.datetime,
        )
    else:
        query = query.order_by(
            desc(models.Product.grade_average),
            desc(models.ProductPrice.value),
            desc(models.Product.datetime),
        )

    if data.page_size and data.page_num:
        query = query.limit(data.page_size).offset((data.page_num - 1) * data.page_size)

    raw_data = (await session.execute(query)).fetchall()

    result_output = response_models.ProductPaginationOut(total_products=0)

    for product_tables in raw_data:
        mapped_tables = {}
        for table in product_tables:
            # add to mapped_tables raw product data with keys:
            # 'products', 'product_prices', 'product_property_values',
            # 'category_property_values', 'suppliers'
            if not table:
                continue
            try:
                mapped_tables[table.__table__.name] = table.__dict__
            except AttributeError as ex:
                pass

        product_data = {
            **mapped_tables.get("products", {}),
        }
        product_prices = mapped_tables.get("product_prices", {})
        product_prices.pop("id", None)
        product_modeled = ProductOut(**{**product_data, **product_prices})

        supplier_data = {
            **mapped_tables.get("suppliers", {}),
            **mapped_tables.get("users", {}),
        }
        supplier_modeled = response_models.SupplierOut(**supplier_data)

        # TODO: rewrite and include to the main query
        image_query = select(models.ProductImage).filter(
            models.ProductImage.product_id == product_modeled.id
        )
        image_data = (await session.execute(image_query)).all()

        if image_data:
            images_modeled = [
                response_models.OneImageOut(**image[0].__dict__) for image in image_data
            ]
        else:
            images_modeled = []

        all_product_data = response_models.AllProductDataOut(
            product=product_modeled, supplier=supplier_modeled, images=images_modeled
        )

        result_output.result.append(all_product_data)

    result_output.total_products = len(result_output.result)
    return result_output.dict()


@products.get(
    "/{product_id}/grades/",
    summary="WORKS: get all review grades by product_id",
    response_model=GradeOut,
)
async def get_grade_and_count(product_id: int):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID",
        )
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCT_NOT_FOUND"
        )
    grade = await Product.get_product_grade(product_id=product_id)
    grade_details = await Product.get_product_grade_details(product_id=product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"grade": grade, "grade_details": grade_details},
    )


@products.patch(
    "/favorite_product/", summary="WORKS: add and remove product in favorite"
)
async def add_remove_favorite_product(
    product_id: int,
    is_favorite: bool,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)

    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_SELLER"
        )

    if is_favorite:
        is_product_favorite = await session.execute(
            select(SellerFavorite).where(SellerFavorite.product_id.__eq__(product_id))
        )
        if is_product_favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PRODUCT_IS_ALREADY_FAVORITE",
            )

        await session.execute(
            insert(SellerFavorite).values(seller_id=seller_id, product_id=product_id)
        )
        status_message = "PRODUCT_ADDED_TO_FAVORITES_SUCCESSFULLY"
    else:
        await session.execute(
            delete(SellerFavorite).where(
                SellerFavorite.seller_id.__eq__(seller_id),
                SellerFavorite.product_id.__eq__(product_id),
            )
        )
        status_message = "PRODUCT_REMOVED_FROM_FAVORITES_SUCCESSFULLY"
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result:": status_message}
    )


@products.put(
    "/change_order_status/{order_product_variation_id}/{status_id}/",
    summary="WORKS: changes the status for the ordered product",
)
async def change_order_status(order_product_variation_id: int, status_id: int):
    try:
        status_order = await OrderStatus.get_status(status_id)
        status_name = status_order.name
        result = await OrderProductVariation.change_status(
            order_product_variation_id, status_id
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "order_product_variation_id": result.id,
                "status_id": result.status_id,
                "status_name": status_name,
            },
        )
    except InvalidStatusId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status id"
        )
    except InvalidProductVariationId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order product variation id",
        )


@products.get("/show_cart/")
async def show_products_cart(
    Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)

    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_SELLER"
        )

    # select stock's and order's product count in seller's cart
    product_variation_count_params = (
        await session.execute(
            select(
                Order.id.label("order_id"),
                ProductVariationCount.product_variation_value1_id,
                ProductVariationCount.count.label("product_count"),
                OrderProductVariation.count.label("order_count"),
            )
            .select_from(Order)
            .join(OrderProductVariation)
            .join(ProductVariationCount)
            .where(Order.seller_id.__eq__(seller_id), Order.is_cart.__eq__(1))
        )
    ).all()

    product_variation_value1_ids = [
        item["product_variation_value1_id"] for item in product_variation_count_params
    ]
    product_count_stock = [
        item["product_count"] for item in product_variation_count_params
    ]
    product_count_order = [
        item["order_count"] for item in product_variation_count_params
    ]

    # select product params by product_variation_value1_ids
    product_params = (
        await session.execute(
            select(
                Product.id.label("product_id"),
                Product.name,
                Product.description,
                ProductPrice.value.label("price"),
            )
            .select_from(ProductVariationValue)
            .join(Product)
            .join(ProductPrice)
            .join(
                ProductVariationCount,
                ProductVariationValue.id
                == ProductVariationCount.product_variation_value1_id,
            )
            .where(ProductVariationValue.id.in_(product_variation_value1_ids))
            .group_by(ProductPrice.product_id)
        )
    ).all()

    result_product_params = []
    for num, product_info in enumerate(product_params):
        product_info = dict(product_info)
        product_info["price"] = float(product_info["price"])
        product_info["product_count_order"] = product_count_order[num]
        product_info["product_count_stock"] = product_count_stock[num]
        result_product_params.append(product_info)

    result = {
        "items": len(product_params),
        "total_count": sum(product_count_order),
        "products": result_product_params,
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": result})
