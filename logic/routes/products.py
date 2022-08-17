from itertools import product
from math import prod
from classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from logic import utils
from logic.consts import *
from database import get_session
from database.models import *
import logging


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
        category_id = await Category.get_category_id(category_name=category)
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
            detail="PRODUCT_NOT_EXIST"
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
        .execute(text(QUERY_FOR_ACTUAL_DEMAND.format(product_id)))
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
            detail="PRODUCT_NOT_EXIST"
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

# return structure:
# {"result": 
#            [
#             {
#              product_id: '',
#              main_info: {QUERY_FOR_PAGINATION},
#              images: {
#                       image_url: '',
#                       serial_num: ''
#                      },
#              supplier: {
#                         customer_name: '',
#                         years: '',
#                         deals: ''
#                        }
#             },
#             {next_product},
#             ...
#            ]
# }
@products.get("/products_list/",  # better /pagination/
        summary='')  # where is summary? and use response_model = ResultOut
async def pagination(page_num: int, page_size: int, category: str = 'all', session: AsyncSession = Depends(get_session)):  # pep8! 79 chars in a row
    if not isinstance(page_num, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PARAMS_FOR_PAGE"
        )
    if not isinstance(page_size, int):  # add to previous if-clause using 'or'
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PARAMS_FOR_PAGE"
        )
    if category == 'all':
        category_id = 'p.category_id'
    else:
        category_id = await Category.get_category_id(category_name=category)  
    param_for_pagination = (page_num - 1) * page_size
    query = await session.\
            execute(QUERY_FOR_PAGINATION.format(category_id, page_size, param_for_pagination))  # pep8
    query = [dict(row) for row in query if query] # why next if-clause is #commented?

    supplier_info = await Supplier.get_supplier_info(product_id='how?')
    # if not category_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="CATEGORY_NOT_FOUND"
    #     )
    if query:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": query}  # change return
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )


@products.get("/grades/",
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
    

@products.post("/make-product-review/",
              summary="")
async def make_product_review(product_review: ProductReviewIn,
                              product_id: int,
                              seller_id: int,
                              session: AsyncSession = Depends(get_session)):
    is_allowed = await session\
        .execute(select(Order.is_completed)\
                 .where(Order.product_id.__eq__(product_id) & Order.seller_id.__eq__(seller_id)))
    is_allowed = is_allowed.scalar()
    current_time = utils.get_moscow_datetime()
    if is_allowed:
        grade_average = await session\
                              .execute(select(Product.grade_average)\
                                       .where(Product.id.__eq__(product_id)))
        grade_average = grade_average.scalar()
        if not grade_average:
            grade_average_new = product_review.product_review_grade
        else:
            review_count = await session\
                             .execute(select(func.count())\
                                      .where(ProductReview.product_id.__eq__(product_id)))
            review_count = review_count.scalar()
            grade_average_new = round((grade_average * review_count + product_review.product_review_grade)\
                                / (review_count + 1), 1)
        await session.execute(update(Product)\
                              .where(Product.id.__eq__(product_id))\
                              .values(grade_average=grade_average_new))
        await session.commit()
        review_data = ProductReview(
            product_id=product_id,
            seller_id=seller_id,
            text=product_review.product_review_text,
            grade_overall=product_review.product_review_grade,
            datetime=current_time
        )
        session.add(review_data)
        await session.commit()
        product_review_id = await session\
                                  .execute(select(ProductReview.id)\
                                           .where(ProductReview.product_id.__eq__(product_id)))
        product_review_id = product_review_id.scalar()
        if product_review.product_review_photo:
            photo_review_data = ProductReviewPhoto(
                product_review_id=product_review_id,
                image_url=product_review.product_review_photo
            )
            session.add(photo_review_data)
            await session.commit()
        await session.execute(delete(Order)\
                              .where(Order.product_id.__eq__(product_id) & Order.seller_id.__eq__(seller_id)))
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "REVIEW_HAS_BEEN_SENT"}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"result": "METHOD_NOT_ALLOWED"}
        )


@products.get("/show-product-review/",
              summary="")
async def get_10_product_reviews(product_id: int,
                             session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="INVALID_PRODUCT_ID"
        )
    product_reviews = await session\
                            .execute(QUERY_FOR_REVIEWS.format(product_id=product_id))
    product_reviews = [dict(text) for text in product_reviews if product_reviews]
    if product_reviews:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=product_reviews
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="REVIEWS_NOT_FOUND"
        )

