from __future__ import annotations
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.suppliers import add_product_info_core
from schemas import BodyProductUploadRequest
from orm import ProductModel



async def test_add_product_info_core(session: AsyncSession):
    request = BodyProductUploadRequest(
        name="Test Product",
        description="This is a test product",
        category_id=1,
        properties=[1, 2],
        variations=[3, 4],
        prices=[
            {
                "value": 9.99,
                "min_quantity": 1,
                "discount": 0,
                "start_date": datetime.now(),
                "end_date": "2099-01-01T00:00:00",
            },
            {
                "value": 8.99,
                "min_quantity": 10,
                "discount": 0.1,
                "start_date": datetime.now(),
                "end_date": "2099-01-01T00:00:00",
            }
        ]
    )
    # user = await crud.users.get.one(session=session, where=[UserModel.id == 1], options=[joinedload(UserModel.supplier)])
    # print(user.id)
    product = await add_product_info_core(request=request, supplier_id=1, session=session)
    print(product.name)
    assert isinstance(product, ProductModel)