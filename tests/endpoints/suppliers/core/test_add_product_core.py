from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from api.routers.suppliers import add_product_info_core
from orm import ProductModel
from schemas import BodyProductUploadRequest


async def test_add_product_info_core(
    session: AsyncSession,
    add_product_request: Dict[str, Any],
    supplier_id: int,
) -> None:
    result = await add_product_info_core(
        request=BodyProductUploadRequest.parse_obj(add_product_request),
        supplier_id=supplier_id,
        session=session,
    )

    assert isinstance(result, ProductModel)
