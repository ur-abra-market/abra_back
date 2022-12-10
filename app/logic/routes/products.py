from app.classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, and_, or_, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.logic.consts import *
from app.database import get_session
from app.database.models import *
from fastapi_jwt_auth import AuthJWT
import json


products = APIRouter()


@products.get(
    "/compilation/",
    summary="WORKS: Get list of products by type "
    "(bestsellers, new, rating, hot) "
    "and category_id (empty or 1-3).",
    response_model=ListOfProductsOut,
)
async def get_products_list_for_category(
    type: str,
    category_id: Optional[int] = None,
    page_num: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_session),
):
    order_by_type = {
        "bestsellers": "p.total_orders",
        "new": "p.datetime",
        "rating": "p.grade_average",
        "hot": "p.total_orders",
    }
    if type not in order_by_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="TYPE_NOT_EXIST"
        )

    if not category_id:
        category_id = "p.category_id"
    else:
        is_category_id_exist = await Category.is_category_id_exist(
            category_id=category_id
        )
        if not is_category_id_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CATEGORY_ID_DOES_NOT_EXIST",
            )
    if type == "hot":
        where_clause = "AND" + WHERE_CLAUSE_IS_ON_SALE
    else:
        where_clause = ""
    products_to_skip = (page_num - 1) * page_size
    products = await session.execute(
        text(
            QUERY_FOR_COMPILATION.format(
                category_id=category_id,
                where_clause=where_clause,
                order_by=order_by_type[type],
                page_size=page_size,
                products_to_skip=products_to_skip,
            )
        )
    )
    products = [dict(row) for row in products if products]
    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": products})


@products.get(
    "/images/",
    summary="WORKS (example 1-100): Get product images by product_id.",
    response_model=ImagesOut,
)
async def get_images_for_product(product_id: int):
    images = await ProductImage.get_images(product_id=product_id)
    if images:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": images})
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="IMAGES_NOT_FOUND"
        )


@products.post(
    "/product_card_p1/",
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
                and_(
                    SellerFavorite.product_id.__eq__(product_id),
                    SellerFavorite.seller_id.__eq__(seller_id),
                )
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


@products.post(
    "/product_card_p2/",
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
    response_model=ListOfProductsOut,
)
async def get_similar_products_in_category(
    product_id: int, session: AsyncSession = Depends(get_session)
):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID",
        )
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCT_DOES_NOT_EXIST"
        )
    category_id = await Product.get_category_id(product_id=product_id)
    products = await session.execute(
        QUERY_FOR_SIMILAR_PRODUCTS.format(
            product_id=product_id, category_id=category_id
        )
    )
    products = [dict(row) for row in products if products]
    if products:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": products}
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_PRODUCTS")


@products.get(
    "/popular/",
    summary="WORKS (example 1-100): Get popular products in this category.",
    response_model=ListOfProductsOut,
)
async def get_popular_products_in_category(
    product_id: int, session: AsyncSession = Depends(get_session)
):
    category_id = await session.execute(
        select(Product.category_id).where(Product.id.__eq__(product_id))
    )
    category_id = category_id.scalar()
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCT_NOT_FOUND"
        )

    products = await session.execute(
        text(
            QUERY_FOR_COMPILATION.format(
                category_id=category_id,
                where_clause="",
                order_by="p.total_orders",
                page_size=6,
                products_to_skip=0,
            )
        )
    )
    products = [dict(row) for row in products if products]
    if products:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": products}
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_PRODUCTS")


@products.post(
    "/pagination/",
    summary="WORKS: Pagination for products list page (sort_type = rating/price/date).",
    response_model=ResultOut,
)
async def pagination(
    data: ProductsPagination,
    session: AsyncSession = Depends(get_session),
):
    sort_type_mapping = dict(
        rating="p.grade_average", price="pp.value", date="p.datetime"
    )
    if data.sort_type not in sort_type_mapping:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="INVALID_SORT_TYPE"
        )

    where_filters = ["WHERE p.is_active = 1"]
    cte = []
    cte_tables = [" "]

    if data.category_id is not None:
        is_category_id_exist = await Category.is_category_id_exist(
            category_id=data.category_id
        )
        if not is_category_id_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CATEGORY_ID_DOES_NOT_EXIST",
            )
        where_filters.append(f"p.category_id = {data.category_id}")
    if data.bottom_price is not None:
        where_filters.append(f"pp.value >= {data.bottom_price}")
    if data.top_price is not None:
        where_filters.append(f"pp.value <= {data.top_price}")
    if data.with_discount:
        where_filters.append(WHERE_CLAUSE_IS_ON_SALE)
    if data.sizes:
        variation_type_id = await CategoryVariationType.get_id(name="size")
        if not variation_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="SIZE_DOES_NOT_EXIST"
            )
        data.sizes = ", ".join([f'"{size}"' for size in data.sizes if data.sizes])
        cte.append(
            QUERY_FOR_PAGINATION_CTE_VARIATION.format(
                type="size", variation_type_id=variation_type_id, type_value=data.sizes
            )
        )
        cte_tables.append("variations_size")
        where_filters.append("p.id = variations_size.product_id")
    if data.brands:
        property_type_id = await CategoryPropertyType.get_id(name="brand")
        if not property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="BRAND_DOES_NOT_EXIST"
            )
        data.brands = ", ".join([f'"{brand}"' for brand in data.brands if data.brands])
        cte.append(
            QUERY_FOR_PAGINATION_CTE_PROPERTY.format(
                type="brand", property_type_id=property_type_id, type_value=data.brands
            )
        )
        cte_tables.append("properties_brand")
        where_filters.append("p.id = properties_brand.product_id")
    if data.materials:
        property_type_id = await CategoryPropertyType.get_id(name="material")
        if not property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="MATERIAL_DOES_NOT_EXIST"
            )
        data.materials = ", ".join(
            [f'"{material}"' for material in data.materials if data.materials]
        )
        cte.append(
            QUERY_FOR_PAGINATION_CTE_PROPERTY.format(
                type="material",
                property_type_id=property_type_id,
                type_value=data.materials,
            )
        )
        cte_tables.append("properties_material")
        where_filters.append("p.id = properties_material.product_id")

    order = "ASC" if data.ascending else "DESC"
    cte_str = "WITH " + ", ".join(cte) if cte else ""
    cte_tables_str = ", ".join(cte_tables)
    where_filters_str = " AND ".join(where_filters)
    products_to_skip = (data.page_num - 1) * data.page_size

    products_result = await session.execute(
        QUERY_FOR_PAGINATION_PRODUCT_ID.format(
            cte=cte_str,
            cte_tables=cte_tables_str,
            where_filters=where_filters_str,
            sort_type=sort_type_mapping[data.sort_type],
            order=order,
            page_size=data.page_size,
            products_to_skip=products_to_skip,
        )
    )
    if not products_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO_PRODUCTS")

    product_ids = list()
    total_products = 0
    for row in products_result:
        product_ids.append(row[0])
        total_products = row[1]
    # this variant is faster /\ this is look better \/
    # products_result = products_result.fetchall()
    # product_ids = [row['id'] for row in products_result]
    # total_products = products_result[0]['total_products']

    result = list()
    for product_id in product_ids:
        main_info = await session.execute(QUERY_FOR_PAGINATION_INFO.format(product_id))
        for row in main_info:
            info = dict(row)
        supplier = await Supplier.get_supplier_info(product_id=product_id)
        images = await ProductImage.get_images(product_id=product_id)
        one_product = dict(
            product_id=product_id, info=info, images=images, supplier=supplier
        )
        result.append(one_product)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"total_products": total_products, "result": result},
    )


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


@products.post("/favorite_product/",
               summary="WORKS: add and remove product in favorite"
               )
async def add_remove_favorite_product(
        product_id: int,
        is_favorite: bool,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())['email']
    seller_id = await Seller.get_seller_id_by_email(user_email)

    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_SELLER"
        )

    if is_favorite:
        is_product_favorite = await session.execute(
            select(SellerFavorite.product_id).
            where(SellerFavorite.product_id.__eq__(product_id))
        )
        is_product_favorite = is_product_favorite.first()
        if is_product_favorite is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PRODUCT_IS_ALREADY_FAVORITE"
            )

        await session.execute(
            insert(SellerFavorite).
            values(seller_id=seller_id, product_id=product_id)
        )
        status_message = "PRODUCT_ADDED_TO_FAVORITES_SUCCESSFULLY"
    else:
        await session.execute(
            delete(SellerFavorite).
            where(and_(
                SellerFavorite.seller_id.__eq__(seller_id),
                SellerFavorite.product_id.__eq__(product_id)
                ))
        )
        status_message = "PRODUCT_REMOVED_FROM_FAVORITES_SUCCESSFULLY"
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result:": status_message}
    )
