from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
import logging


products = APIRouter()


@products.post("/", summary='WORKS: Get list of products by type (bestsellers, new, rating, hot, popular) and category (all, clothes)',
                response_model=MainPageProductsOut)
async def get_products_list_for_category(type: str, category: str = 'clothes'):
    result = await c.get_products_list_for_category(type=type, category=category)
    return result
