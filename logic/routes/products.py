from math import prod
from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
import logging


products = APIRouter()


@products.get("/compilation/", summary='WORKS: Get list of products by type (bestsellers, new, rating, hot, popular) and category (all, clothes).',
                response_model=MainPageProductsOut)
async def get_products_list_for_category(type: str, category: str = 'all'):
    result = await c.get_products_list_for_category(type=type, category=category)
    return result


@products.get("/images/", summary='WORKS: Get product images by product_id.')
async def get_images_for_product(product_id: int):
    result = await c.get_images_for_product(product_id=product_id)
    return result