import datetime
import json
from datetime import datetime
from typing import List, Optional

import pytz
from sqlalchemy import delete, desc, func, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.database import models
from app.schemas import UserSchema, request_schemas, test_schemas


class ProductRepo:

    async def _get_suppliers_products(self, supplier_id:int, session:AsyncSession)->Optional[schemas.ListOfProductsOut]:
        query = select(models.Product).filter(models.Product.supplier_id == supplier_id)
        product_res = await session.execute(query)
        products = product_res.all()
        if not products:
            return []
        breakpoint()
        pr = products[0][0]
        products = [schemas.ProductOut(**pr[0].__dict__) for pr in products]
        return schemas.ListOfProductsOut(result=products)      

    async def pagination(self, request_params: request_schemas.ProductsPaginationRequest, session:AsyncSession):
        query = (
            select(
                models.Product
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
            .outerjoin(models.Supplier, models.Product.supplier_id == models.Supplier.id)
            .outerjoin(models.User, models.Supplier.user_id == models.User.id)
            .outerjoin(
                models.ProductVariationValue,
                models.ProductVariationValue.product_id == models.Product.id,
            )
            .outerjoin(
                models.CategoryVariationValue,
                models.ProductVariationValue.variation_value_id
                == models.CategoryVariationValue.id,
            ).\
            outerjoin(models.CategoryVariationType,models.CategoryVariationType.id==models.CategoryVariationValue.variation_type_id)
            .filter(models.Product.is_active == 1)
                # .filter(models.Product.id == 1) #TODO: убрать!
        )

        if request_params.category_id:
            query = query.filter(models.Category.id == request_params.category_id)

        if request_params.sizes:
            query = query.filter(models.CategoryVariationType.name=='Size',
                                 models.CategoryVariationValue.value.in_(request_params.sizes)
        )

        now = datetime.now(tz=pytz.timezone("Europe/Moscow")).replace(tzinfo=None)

        query = query.filter(models.ProductPrice.start_date < now).filter(
            func.coalesce(models.ProductPrice.end_date, datetime(year=2099, month=1, day=1))
            > now
        )

        if request_params.bottom_price is not None:
            query = query.filter(models.ProductPrice.value >= request_params.bottom_price)
        if request_params.top_price is not None:
            query = query.filter(models.ProductPrice.value <= request_params.bottom_price)
        if request_params.with_discount:
            query = query.filter(func.coalesce(models.ProductPrice.discount, 0) > 0)

        if request_params.materials:
            query = query.filter(models.CategoryPropertyValue.value.in_(request_params.materials))

        if request_params.ascending:
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

        if request_params.page_size and request_params.page_num:
            query = query.limit(request_params.page_size).offset((request_params.page_num - 1) * request_params.page_size)

        raw_products = (await session.execute(query)).unique().all()
        modeled_products = [test_schemas.Product.from_orm(prod[0]) for prod in raw_products]
        raw_pr  = raw_products[0][0]
        # print(modeled_products)
        # breakpoint()
        # return modeled_products
        return test_schemas.PaginatedProducts(total=len(modeled_products), products=modeled_products)

    async def get_suppliers_products(self, supplier_id:int, session:AsyncSession)->Optional[schemas.ListOfProductsOut]:
        # columns  = models.Product.__table__.columns #+ models.Supplier.__table__.columns
        # product_res = await session.execute(select(*columns).filter(models.Product.supplier_id == supplier_id))
        # res = product_res.all()

        query = (
        select(
            models.Product
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
        .outerjoin(models.Supplier, models.Product.supplier_id == models.Supplier.id)
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
        .filter(models.Product.is_active == 1).filter(models.CategoryVariationValue.id==1)
    )

        
        res = (await session.execute(query)).unique().all()
        modeled_products = [test_schemas.Product.from_orm(prod[0]) for prod in res]
        
        # prod_1 = res[0][0]
        # modeled_product = test_schemas.Product.from_orm(prod_1)
        # sup = prod_1.supplier
        # print(sup)

        # sup_modeled=test_schemas.Supplier).from_orm(sup)
        breakpoint()
        print(res)
        return res
        

    # columns = Appointments.__table__.columns+ [Clients.name, Client.other_column] db.session.query(*columns) – 

product_repo = ProductRepo()