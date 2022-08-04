from classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from database import get_session
from database.models import *



products = APIRouter()


@products.get("/compilation/", 
    summary='WORKS: Get list of products by type'
            '(bestsellers, new, rating, hot, popular)'
            'and category (all, clothes).',
    response_model=ListOfProductsOut)
async def get_products_list_for_category(type: str,
                                category: str = 'all',
                                session: AsyncSession = Depends(get_session)):
    query_by_type = {'bestsellers': SQL_QUERY_FOR_BESTSELLERS, 
                     'new': SQL_QUERY_FOR_NEW_ARRIVALS,
                     'rating': SQL_QUERY_FOR_HIGHEST_RATINGS,
                     'hot': SQL_QUERY_FOR_HOT_DEALS,
                     'popular': SQL_QUERY_FOR_POPULAR_NOW}
    if type not in query_by_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TYPE_NOT_EXIST"
        )

    if category == 'all':
        category_id = 'p.category_id'
    else:
        category_id = await session\
                    .execute(select(Category.id)\
                    .where(Category.name.__eq__(category)))
        category_id = category_id.scalar()
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )

    products = await session.\
            execute(text(query_by_type[type].format(category_id)))
    products = [dict(row) for row in products if products]
    return JSONResponse(
        status_code=200,
        content={"result": products}
    )


@products.get("/images/", 
              summary='WORKS (example 20): Get product images by product_id.',
              response_model=ImagesOut)
async def get_images_for_product(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    images = await session\
        .execute(select(ProductImage.image_url, ProductImage.serial_number)\
        .where(ProductImage.product_id.__eq__(product_id)))
    images = [dict(image_url=row[0], serial_number=row[1])\
              for row in images if images]
    if images:
        return JSONResponse(
            status_code=200,
            content={"result": images}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )


@products.get("/similar/",
            summary='WORKS (example 20): Get similar products by product_id.',
            response_model=ListOfProductsOut)
async def get_similar_products_in_category(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="INVALID_PRODUCT_ID"
        )
    products = await session.\
           execute(SQL_QUERY_FOR_SIMILAR_PRODUCTS.format(product_id))
    products = [dict(row) for row in products if products]
    if products:
        return JSONResponse(
            status_code=200,
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
            .execute(text(SQL_QUERY_FOR_POPULAR_NOW.format(category_id)))
    products = [dict(row) for row in products if products]
    if products:
        return JSONResponse(
            status_code=200,
            content={"result": products}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )
