from app.classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.logic import utils
from app.logic.consts import *
from app.database import get_session
from app.database.models import *


products = APIRouter()


@products.get("/compilation/", 
    summary='WORKS: Get list of products by type '
            '(bestsellers, new, rating, hot) '
            'and category_id (empty or 1-3).',
    response_model=ListOfProductsOut)
async def get_products_list_for_category(type: str,
                                category_id: int = None,
                                page_num: int = 1,
                                page_size: int = 10,
                                session: AsyncSession = Depends(get_session)):
    order_by_type = {'bestsellers': 'p.total_orders', 
                     'new': 'p.datetime',
                     'rating': 'p.grade_average',
                     'hot': 'p.total_orders'}
    if type not in order_by_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TYPE_NOT_EXIST"
        )

    if not category_id:
        category_id = 'p.category_id'
    else:
        is_category_id_exist = await Category.is_category_id_exist(category_id=category_id)
        if not is_category_id_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CATEGORY_ID_DOES_NOT_EXIST"
            )

    where_clause = 'AND p.with_discount = 1' if type == 'hot' else ''
    products_to_skip = (page_num - 1) * page_size
    products = await session.\
            execute(text(QUERY_FOR_COMPILATION.format(category_id=category_id,
                                                    where_clause=where_clause,
                                                    order_by=order_by_type[type],
                                                    page_size=page_size,
                                                    products_to_skip=products_to_skip)))
    products = [dict(row) for row in products if products]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": products}
    )


@products.get("/images/", 
              summary='WORKS (example 1-100): Get product images by product_id.',
              response_model=ImagesOut)
async def get_images_for_product(product_id: int):
    images = await ProductImage.get_images(product_id=product_id)
    if images:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": images}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IMAGES_NOT_FOUND"
        )


@products.get("/product_card_p1/",
        summary='WORKS (example 1-100, 1): Get info for product card p1.',
        response_model=ResultOut)
async def get_info_for_product_card(product_id: int,
                                    seller_id: int,
                                session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
        )
    is_exist = await Product.is_product_exist(product_id=product_id)
    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )

    grade = await Product.get_product_grade(product_id=product_id)

    category = await session\
        .execute(select(Category.name).join(Product)\
        .where(Product.id.__eq__(product_id)))
    category = category.scalar()
    category_path = await Category.get_category_path(category=category)

    product_name = await session\
        .execute(select(Product.name)\
        .where(Product.id.__eq__(product_id)))
    product_name = product_name.scalar()

    is_favorite = await session\
        .execute(select(SellerFavorite.id)\
        .where(and_(SellerFavorite.product_id.__eq__(product_id), 
                    SellerFavorite.seller_id.__eq__(seller_id))))
    is_favorite = bool(is_favorite.scalar())

    color = await session\
        .execute(text(QUERY_FOR_COLORS.format(product_id)))
    color = [dict(row) for row in color if color]

    actual_demand = await session\
        .execute(text(QUERY_FOR_ACTUAL_DEMAND.format(product_id=product_id)))
    actual_demand = actual_demand.scalar()
    actual_demand = actual_demand if actual_demand else '0'

    prices = await session\
        .execute(text(QUERY_FOR_PRICES.format(product_id)))
    prices = [dict(row) for row in prices if prices]

    supplier_info = await Supplier.get_supplier_info(product_id=product_id)

    result = dict(grade=grade,
                  category_path=category_path,
                  product_name=product_name,
                  is_favorite=is_favorite,
                  color=color,
                  actual_demand=actual_demand,
                  prices=prices,
                  supplier_info=supplier_info
                  )
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": result}
        ) 


@products.get("/product_card_p2/",
        summary='WORKS (example 1-100): Get info for product card p2.',
        response_model=ResultOut)
async def get_info_for_product_card(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
        )
    is_exist = await Product.is_product_exist(product_id=product_id)
    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )

    variations = await session\
        .execute(text(QUERY_FOR_VARIATIONS.format(product_id)))
    variations = \
        [dict(row) for row in variations if variations]
    
    # properties for about_the_product and tags
    properties = await session\
        .execute(text(QUERY_FOR_PROPERTIES.format(product_id)))
    properties = \
        [dict(row) for row in properties if properties]

    description = await session\
        .execute(select(Product.description)\
        .where(Product.id.__eq__(product_id)))
    description = description.scalar()

    result = dict(variations=variations,
                  properties=properties,
                  description=description
                  )
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": result}
        )
    


@products.get("/similar/",
            summary='WORKS (example 1-100): Get similar products by product_id.',
            response_model=ListOfProductsOut)
async def get_similar_products_in_category(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
        )
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_DOES_NOT_EXIST"
        )
    category_id = await Product.get_category_id(product_id=product_id)
    products = await session.\
           execute(QUERY_FOR_SIMILAR_PRODUCTS.format(product_id=product_id,
                                                     category_id=category_id))
    products = [dict(row) for row in products if products]
    if products:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": products}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )


@products.get("/popular/",
        summary='WORKS (example 1-100): Get popular products in this category.',
        response_model=ListOfProductsOut)
async def get_popular_products_in_category(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    category_id = await session\
                .execute(select(Product.category_id)\
                .where(Product.id.__eq__(product_id)))
    category_id = category_id.scalar()
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )

    products = await session\
            .execute(text(QUERY_FOR_COMPILATION.format(category_id=category_id,
                                                     where_clause='',
                                                     order_by='p.total_orders',
                                                     page_size=6,
                                                     products_to_skip=0)))
    products = [dict(row) for row in products if products]
    if products:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": products}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )


@products.get("/pagination/",
        summary='WORKS: Pagination for products list page (sort_type = rating or price or date).',
        response_model = ResultOut)
async def pagination(page_num: int = 1,
                     page_size: int = 10,
                     category_id: int = None,
                     sort_type: str = 'rating',
                     ascending: bool = False,
                     bottom_price: int = 0,
                     top_price: int = 0,
                     with_discount: bool = False,
                     size: str = '',
                     brand: str = '',
                     material: str = '',
                     session: AsyncSession = Depends(get_session)):
    sort_type_mapping = dict(rating='p.grade_average',
                             price='pp.value',
                             date='p.datetime')
    if not isinstance(page_num, int) \
        or not isinstance(page_size, int) \
        or not isinstance(bottom_price, int) \
        or not isinstance(top_price, int) \
        or not isinstance(with_discount, bool) \
        or not isinstance(ascending, bool) \
        or not sort_type in sort_type_mapping:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PARAMS_FOR_PAGE"
        )

    where_filters = ['WHERE p.is_active = 1']
    cte = []
    cte_tables = [' ']

    if category_id:
        is_category_id_exist = await Category.is_category_id_exist(category_id=category_id)  
        if not is_category_id_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CATEGORY_ID_DOES_NOT_EXIST"
            )
        where_filters.append(f'p.category_id = {category_id}')
    if bottom_price:
        where_filters.append(f'pp.value >= {bottom_price}')
    if top_price:
        where_filters.append(f'pp.value <= {top_price}')
    if with_discount:
        where_filters.append('p.with_discount = 1')
    if size:
        property_type_id = await CategoryPropertyType.get_id(name='size')
        if not property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SIZE_DOES_NOT_EXIST"
            )
        cte.append(QUERY_FOR_PAGINATION_CTE.format(type='size',
                                                   property_type_id=property_type_id, 
                                                   type_value=size))
        cte_tables.append('properties_size')
        where_filters.append('p.id = properties_size.product_id')
    if brand:
        property_type_id = await CategoryPropertyType.get_id(name='brand')
        if not property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BRAND_DOES_NOT_EXIST"
            )
        cte.append(QUERY_FOR_PAGINATION_CTE.format(type='brand',
                                                   property_type_id=property_type_id, 
                                                   type_value=brand))
        cte_tables.append('properties_brand')
        where_filters.append('p.id = properties_brand.product_id')
    if material:
        property_type_id = await CategoryPropertyType.get_id(name='material')
        if not property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MATERIAL_DOES_NOT_EXIST"
            )
        cte.append(QUERY_FOR_PAGINATION_CTE.format(type='material',
                                                   property_type_id=property_type_id, 
                                                   type_value=material))
        cte_tables.append('properties_material')
        where_filters.append('p.id = properties_material.product_id')

    order = 'ASC' if ascending else 'DESC'
    cte = 'WITH ' + ', '.join(cte) if cte else ''
    cte_tables = ', '.join(cte_tables)
    where_filters = ' AND '.join(where_filters)
    products_to_skip = (page_num - 1) * page_size

    products_result = await session\
        .execute(QUERY_FOR_PAGINATION_PRODUCT_ID\
        .format(cte=cte,
                cte_tables=cte_tables,
                where_filters=where_filters, 
                sort_type=sort_type_mapping[sort_type],
                order=order,
                page_size=page_size, 
                products_to_skip=products_to_skip))
    if not products_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )

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
        main_info = await session\
            .execute(QUERY_FOR_PAGINATION_INFO.format(product_id))
        for row in main_info:
            info = dict(row)
        supplier = await Supplier.get_supplier_info(product_id=product_id)
        images = await ProductImage.get_images(product_id=product_id)
        one_product = dict(product_id=product_id,
                           info=info,
                           images=images,
                           supplier=supplier)
        result.append(one_product)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"total_products": total_products,
                 "result": result}
    )


@products.get("/{product_id}/grades/",
    summary="WORKS: get all review grades by product_id",
    response_model=GradeOut)
async def get_grade_and_count(product_id: int):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
        )
    is_product_exist = await Product.is_product_exist(product_id=product_id)
    if not is_product_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )
    grade = await Product.get_product_grade(product_id=product_id)
    grade_details = await Product.get_product_grade_details(product_id=product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"grade": grade,
                 "grade_details": grade_details}
    )
