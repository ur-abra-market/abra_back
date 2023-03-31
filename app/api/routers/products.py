from fastapi import APIRouter
from fastapi.param_functions import Depends
from starlette import status
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from orm import (
    ProductModel,
    ProductReviewModel,
)
from core.depends import auth_optional, UserObjects, get_session
from core.tools import store
from schemas import (
    ApplicationResponse,
    ProductReviewGradesOut,
)

router = APIRouter()


# @router.get(
#     "/compilation/",
#     summary="WORKS: Get list of products",
#     description="Available filters: total_orders, date, price, rating",
#     response_model=response_models.ProductPaginationOut,
# )
# async def get_products_list_for_category(
#     request_params: request_models.RequestPagination = Depends(
#         request_models.ProductsCompilationRequest
#     ),
#     session: AsyncSession = Depends(get_session),
# ):
#     # TODO: Maybe unite this route with POST /pagination ?
#     query = (
#         select(
#             models.Product,
#             models.ProductPrice,
#         )
#         .outerjoin(
#             models.ProductPrice, models.ProductPrice.product_id == models.Product.id
#         )
#         .filter(models.Product.is_active == 1)
#     )

#     if request_params.category_id:
#         query = query.filter(models.Product.category_id == request_params.category_id)

#     product_sorting_types_map = {
#         "rating": models.Product.grade_average,
#         "price": models.ProductPrice.value,
#         "date": models.Product.datetime,
#         "total_orders": models.Product.total_orders,
#     }

#     if request_params.order_by:
#         request_params.order_by: consts.SortingTypes
#         # convert human readable sort type to field in DB
#         order_by_field = product_sorting_types_map.get(
#             request_params.order_by.value, None
#         )

#         if order_by_field and request_params.order_by.value == "date":
#             query = query.order_by(desc(order_by_field))
#         elif order_by_field and request_params.order_by.value != "date":
#             query = query.order_by(order_by_field)

#     # pagination
#     if request_params.page_size and request_params.page_num:
#         query = query.limit(request_params.page_size).offset(
#             (request_params.page_num - 1) * request_params.page_size
#         )

#     raw_data = (await session.execute(query)).fetchall()
#     result_output = response_models.ProductPaginationOut(total_products=0)

#     # serialization
#     for product_tables in raw_data:
#         mapped_tables = {}
#         for table in product_tables:
#             # add to mapped_tables raw product data with keys:
#             # 'products', 'product_prices', 'images',
#             if not table:
#                 continue
#             try:
#                 mapped_tables[table.__table__.name] = table.__dict__
#             except AttributeError as ex:
#                 pass

#         product_data = {
#             **mapped_tables.get("products", {}),
#         }
#         product_prices = mapped_tables.get("product_prices", {})
#         product_prices.pop("id", None)
#         product_modeled = response_models.ProductOut(
#             **{**product_data, **product_prices}
#         )

#         image_query = select(models.ProductImage).filter(
#             models.ProductImage.product_id == product_modeled.id
#         )
#         image_data = (await session.execute(image_query)).all()
#         if image_data:
#             images_modeled = [
#                 response_models.OneImageOut(**image[0].__dict__) for image in image_data
#             ]
#         else:
#             images_modeled = []

#         all_product_data = response_models.AllProductDataOut(
#             product=product_modeled, images=images_modeled
#         )

#         result_output.result.append(all_product_data)

#     result_output.total_products = len(result_output.result)
#     return result_output.dict()


@router.get(
    path="/{product_id}/grades/",
    dependencies=[Depends(auth_optional)],
    summary="WORKS: get all reviews grades information",
    response_model=ApplicationResponse[ProductReviewGradesOut],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    grade_info = await store.orm.products.get_one(
        ProductModel.grade_average,
        func.count(ProductReviewModel.id),
        session=session,
        where=[ProductModel.id == product_id],
        options=[
            joinedload(ProductModel.reviews),
        ],
        group_by=[ProductModel.grade_average],
    )

    review_details = await store.orm.products.get_many(
        ProductReviewModel.grade_overall,
        func.count(ProductReviewModel.id),
        session=session,
        where=[ProductModel.id == product_id],
        options=[
            joinedload(ProductModel.reviews),
        ],
        group_by=[ProductReviewModel.grade_overall],
        order_by=[ProductReviewModel.grade_overall.desc()],
    )

    return {
        "ok": True,
        "result": {
            "grade_average": grade_info.grade_average,
            "review_count": grade_info.count,
            "details": review_details,
        },
    }
