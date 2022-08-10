from math import prod
from classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from database import get_session
from database.models import *


products = APIRouter()


@products.get("/compilation/", 
    summary='WORKS: Get list of products by type '
            '(bestsellers, new, rating, hot, popular) '
            'and category (all, clothes).',
    response_model=ListOfProductsOut)
async def get_products_list_for_category(type: str,
                                category: str = 'all',
                                session: AsyncSession = Depends(get_session)):
    query_by_type = {'bestsellers': QUERY_FOR_BESTSELLERS, 
                     'new': QUERY_FOR_NEW_ARRIVALS,
                     'rating': QUERY_FOR_HIGHEST_RATINGS,
                     'hot': QUERY_FOR_HOT_DEALS,
                     'popular': QUERY_FOR_POPULAR_NOW}
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
        status_code=status.HTTP_200_OK,
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
            status_code=status.HTTP_200_OK,
            content={"result": images}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCT_NOT_FOUND"
        )


@products.get("/product_card_p1/",
        summary='')
        #response_model=ListOfProductsOut)
async def get_info_for_product_card(product_id: int,
                                    seller_id: int,
                                session: AsyncSession = Depends(get_session)):
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

    prices = await session\
        .execute(select(ProductPrice.value, 
                        ProductPrice.quantity, 
                        ProductPrice.discount)\
        .where(ProductPrice.product_id.__eq__(product_id)))
    prices = prices.scalars().all()



@products.get("/product_card_p2/",
        summary='')
        #response_model=ListOfProductsOut)
async def get_info_for_product_card(product_id: int,
                                session: AsyncSession = Depends(get_session)):
    variations = await session\
        .execute(text(QUERY_FOR_VARIATONS.format(product_id)))
    variations = \
        [dict(row) for row in variations if variations]
    
    about_the_product = await session\
        .execute(text(QUERY_FOR_PROPERTIES.format(product_id)))
    about_the_product = \
        [dict(row) for row in about_the_product if about_the_product]

    description = await session\
        .execute(select(Product.description)\
        .where(Product.id.__eq__(product_id)))
    description = description.scalar()


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
           execute(QUERY_FOR_SIMILAR_PRODUCTS.format(product_id))
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
            .execute(text(QUERY_FOR_POPULAR_NOW.format(category_id)))
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
