from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
import logging


categories = APIRouter()


@categories.get("/", summary='WORKS: Get category path (route) by its name (e.g. try "stove").',
                response_model=CategoryPath)
async def get_category_path(category: str):
    result = await c.get_category_path(category=category)
    return result
