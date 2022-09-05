from classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from logic import utils
from logic.consts import *
from database import get_session
from database.models import *


products = APIRouter()


@products.get("/compilation/", 
    summary='WORKS: Get list of products by type '
            '(bestsellers, new, rating, hot) '
            'and category (all, clothes).',
    response_model=ListOfProductsOut)
async def get_products_list_for_category(type: str,
                                category: str = '',
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

    if not category:
        category_id = 'p.category_id'
    else:
        category_id = await Category.get_category_id(category_name=category)
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
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
              summary='WORKS (example 20): Get product images by product_id.',
              response_model=ImagesOut)
async def get_images_for_product(product_id: int,
                                session: AsyncSession = Depends(get_session)):
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
        summary='WORKS (example 16, 30): Get info for product card p1.',
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
        summary='WORKS (example 16): Get info for product card p2.',
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
        .execute(text(QUERY_FOR_VARIATONS.format(product_id)))
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
            summary='WORKS (example 20): Get similar products by product_id.',
            response_model=ListOfProductsOut)
async def get_similar_products_in_category(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
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
        summary='WORKS (example 20): Get popular products in this category.',
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
async def pagination(page_num: int,
                     page_size: int,
                     category: str = '',
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

    where_filters = ['WHERE 1=1']
    cte = []
    cte_tables = [' ']

    if category:
        category_id = await Category.get_category_id(category_name=category)  
        if not category_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CATEGORY_NOT_FOUND"
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
        cte.append(QUERY_FOR_PAGINATION_CTE.format(type='size',
                                                   property_type_id=property_type_id, 
                                                   type_value=size))
        cte_tables.append('properties_size')
        where_filters.append('p.id = properties_size.product_id')
    if brand:
        property_type_id = await CategoryPropertyType.get_id(name='brand')
        cte.append(QUERY_FOR_PAGINATION_CTE.format(type='brand',
                                                   property_type_id=property_type_id, 
                                                   type_value=brand))
        cte_tables.append('properties_brand')
        where_filters.append('p.id = properties_brand.product_id')
    if material:
        property_type_id = await CategoryPropertyType.get_id(name='material')
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

    product_ids = await session\
        .execute(QUERY_FOR_PAGINATION_PRODUCT_ID\
        .format(cte=cte,
                cte_tables=cte_tables,
                where_filters=where_filters, 
                sort_type=sort_type_mapping[sort_type],
                order=order,
                page_size=page_size, 
                products_to_skip=products_to_skip))
    if not product_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )
    product_ids = [row[0] for row in product_ids]

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
        content={"result": result}
    )


@products.get("/{product_id}/grades/",
    summary="WORKS (example 2): get all review grades by product_id",
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


@products.post("/add_main_product_info/",
    summary="WORKS: Add product to database. Images in [url0, url1 ...] format (optional)."
            "type_name is category name (example 'clothes')!",
    response_model=ProductIdOut)
async def add_product_info_to_db(supplier_id: int,
                            product_name: str,
                            type_name: str,
                            image_urls: list = list(),
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
        content={"product_id": product_id}
    )


@products.get("/get_product_properties/",
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
    

@products.post("/add_product_properties/",
    summary="WORKS: Add properties to database. "
            "Properties in {'name': 'value', ...} format. "
            "Names sctricly from /products/get_product_properties/ route. "
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


@products.post("/add_product_prices/",
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
    