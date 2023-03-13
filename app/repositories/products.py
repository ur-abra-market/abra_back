from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.database import models 
from app import schemas 
from app.schemas import UserSchema


class ProductRepo:

    async def get_suppliers_products(self, supplier_id:int, session:AsyncSession)->Optional[schemas.ListOfProductsOut]:
        query = select(models.Product).filter(models.Product.supplier_id == supplier_id)
        product_res = await session.execute(query)
        products = product_res.all()
        if not products:
            return []
        products = [schemas.ProductOut(**pr[0].__dict__) for pr in products]
        return schemas.ListOfProductsOut(result=products)         

product_repo = ProductRepo()