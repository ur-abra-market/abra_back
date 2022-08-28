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
    images = await ProductImage.get_images(product_id=product_id)
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


@products.get("/pagination/",
        summary='WORKS: Pagination for products list page (sort_type = rating or price or date).',
        response_model = ResultOut)
async def pagination(page_num: int,
                     page_size: int,
                     category: str = 'all',
                     bottom_price: int = 0,
                     top_price: int = 0,
                     with_discount: bool = False,
                     sort_type: str = 'rating',
                     ascending: bool = False,
                     session: AsyncSession = Depends(get_session)):
    sort_type_mapping = dict(rating='p.grade_average',
                             price='pp.value',
                             date='p.datetime')
    if not isinstance(page_num, int) \
        or not isinstance(page_size, int)\
        or not isinstance(bottom_price, int)\
        or not isinstance(top_price, int)\
        or not isinstance(with_discount, bool)\
        or not isinstance(ascending, bool)\
        or not sort_type in sort_type_mapping:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PARAMS_FOR_PAGE"
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
    where_filters = ''
    if bottom_price:
        where_filters += f'AND pp.value >= {bottom_price} '
    if top_price:
        where_filters += f'AND pp.value <= {top_price} '
    if with_discount:
        where_filters += 'AND p.with_discount = 1 '
    if ascending:
        order = 'ASC'
    else:
        order = 'DESC'

    param_for_pagination = (page_num - 1) * page_size
    product_ids = await session\
        .execute(QUERY_FOR_PAGINATION_PRODUCT_ID\
        .format(category_id=category_id, 
                where_filters=where_filters, 
                sort_type=sort_type_mapping[sort_type],
                order=order,
                page_size=page_size, 
                param_for_pagination=param_for_pagination))
    product_ids = [row[0] for row in product_ids if product_ids]
    if not product_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NO_PRODUCTS"
        )

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
    

@products.post("/{product_id}/make-product-review/",
              summary="WORKS: query params(product_id, seller_id) count new average grade, sends reviews")
async def make_product_review(product_review: ProductReviewIn,
                              product_id: int,
                              seller_id: int,
                              session: AsyncSession = Depends(get_session)):
    is_allowed = await session\
        .execute(select(Order.id)\
                 .where(Order.product_id.__eq__(product_id) \
                      & Order.seller_id.__eq__(seller_id) \
                      & Order.status_id.__eq__(4)))
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
        # next execute() need to change because of is_completed
        await session.execute(update(Order)\
                              .where(Order.product_id.__eq__(product_id) & Order.seller_id.__eq__(seller_id))\
                              .values(is_completed=0))
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


@products.get("/{product_id}/show-product-review/",
              summary="WORKS: get product_id, skip(def 0), limit(def 10), returns reviews")
async def get_10_product_reviews(product_id: int,
                                 skip: int = 0,
                                 limit: int = 10,
                                 session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
        )
    if limit:
        quantity = f"LIMIT {limit} OFFSET {skip}"
        product_reviews = await session\
                                .execute(QUERY_FOR_REVIEWS.format(product_id=product_id, quantity=quantity))
    else:
        quantity = ""
        product_reviews = await session\
                                .execute(QUERY_FOR_REVIEWS.format(product_id=product_id, quantity=quantity))
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


@products.post("/{product_review_id}/product-review-reactions/",
              summary="WORKS: query params(product_review_id and seller_id), body (reaction), insert reaction data")
async def make_reaction(product_review_id: int,
                        seller_id: int,
                        reaction: ReactionIn,
                        session: AsyncSession = Depends(get_session)):
    reaction_data = ProductReviewReaction(
        seller_id=seller_id,
        product_review_id=product_review_id,
        reaction=reaction.reaction
    )
    session.add(reaction_data)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "REACTION_HAS_BEEN_SENT"}
    )