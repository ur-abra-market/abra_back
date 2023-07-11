from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.suppliers import add_product_info_core
from orm import ProductModel, UserModel
from schemas.uploads import ProductUpload
from typing_ import DictStrAny


async def test_add_product_info_core(
    session: AsyncSession,
    add_product_request: DictStrAny,
    pure_supplier: UserModel,
) -> None:
    result = await add_product_info_core(
        request=ProductUpload.parse_obj(add_product_request),
        supplier_id=pure_supplier.supplier.id,
        session=session,
    )

    assert isinstance(result, ProductModel)
