import json

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import select, text, delete, insert, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
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
    "/compilation",
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

    if request_params.order_by:
        request_params.order_by: consts.SortingTypes
        # convert human readable sort type to field in DB
        order_by_field = consts.product_sorting_types_map.get(
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
    "/product_card_p1/{product_id}",
    summary="WORKS (example 1-100, 1): Get info for product card p1.",
    response_model=ResultOut,
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

    grade = await Product.get_product_grade(product_id=product_id)

    category_params = await session.execute(
        select(Category.id, Category.name)
        .join(Product)
        .where(Product.id.__eq__(product_id))
    )
    category_id, category_name = category_params.fetchone()
    category_path = await Category.get_category_path(category=category_name)

    product_name = await session.execute(
        select(Product.name).where(Product.id.__eq__(product_id))
    )
    product_name = product_name.scalar()

    tags = await Tags.get_tags_by_product_id(product_id=product_id)

    colors = await session.execute(text(QUERY_FOR_COLORS.format(product_id=product_id)))
    colors = [row[0] for row in colors if colors]

    sizes = await session.execute(text(QUERY_FOR_SIZES.format(product_id=product_id)))
    sizes = [row[0] for row in sizes if sizes]

    monthly_actual_demand = await session.execute(
        text(QUERY_FOR_MONTHLY_ACTUAL_DEMAND.format(product_id=product_id))
    )
    monthly_actual_demand = monthly_actual_demand.scalar()
    monthly_actual_demand = monthly_actual_demand if monthly_actual_demand else "0"

    daily_actual_demand = await session.execute(
        text(QUERY_FOR_DAILY_ACTUAL_DEMAND.format(product_id=product_id))
    )
    daily_actual_demand = daily_actual_demand.scalar()
    daily_actual_demand = daily_actual_demand if daily_actual_demand else "0"

    prices = await session.execute(text(QUERY_FOR_PRICES.format(product_id)))
    prices = [dict(row) for row in prices if prices]

    supplier_info = await Supplier.get_supplier_info(product_id=product_id)

    result = dict(
        grade=grade,
        category_id=category_id,
        category_path=category_path,
        product_name=product_name,
        is_favorite=is_favorite,
        tags=tags,
        colors=colors,
        sizes=sizes,
        monthly_actual_demand=monthly_actual_demand,
        daily_actual_demand=daily_actual_demand,
        prices=prices,
        supplier_info=supplier_info,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": result})


@products.get(
    "/product_card_p2/{product_id}",
    summary="WORKS (example 1-100): Get info for product card p2.",
    response_model=ResultOut,
)
async def get_info_for_product_card_p2(
    product_id: int, session: AsyncSession = Depends(get_session)
):
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

    variations = await session.execute(text(QUERY_FOR_VARIATIONS.format(product_id)))
    variations = [dict(row) for row in variations if variations]

    # properties for about_the_product and tags
    properties = await session.execute(text(QUERY_FOR_PROPERTIES.format(product_id)))
    properties = [dict(row) for row in properties if properties]

    description = await session.execute(
        select(Product.description).where(Product.id.__eq__(product_id))
    )
    description = description.scalar()

    result = dict(variations=variations, properties=properties, description=description)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": result})


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


@products.post("/add_to_cart/", summary="WORKS: adding a product to the cart")
async def add_to_cart(
    product_variation_count_id: int,
    count: int,
    Authorize: AuthJWT = Depends(),
):
    try:
        Authorize.jwt_required()
        user_email = json.loads(Authorize.get_jwt_subject())["email"]
        seller_id = await Seller.get_seller_id_by_email(user_email)

        if not seller_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="USER_NOT_SELLER"
            )

        order_product_variation_count, product_variation_count = \
            await OrderProductVariation.add_to_cart(
                product_variation_count_id, count, seller_id
            )
    except ProductVariationCountIdException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product variation count id",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NOT_ENOUGH_PRODUCTS_IN_STOCK",
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "products_count_in_stock": product_variation_count,
            "products_count_in_order": order_product_variation_count,
        },
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
