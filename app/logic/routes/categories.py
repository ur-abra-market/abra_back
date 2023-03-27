from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.logic.consts import *
from app.logic.queries import *
from app.database.models import *
import app.logic.memory as memory

categories = APIRouter()


def process_childs(parent_path, childs, data):
    for child in childs:
        id = child["id"]
        childs = data.get(id, [])
        child["path"] = ""
        if parent_path:
            child["path"] = parent_path + "|"
        child["path"] += child["name"]
        child["childs"] = childs
        process_childs(child["path"], childs, data)


@categories.on_event("startup")
async def load_categories():
    all_categories = await Category.get_all_categories()
    temp = {}
    for item in all_categories:
        key = item["parent_id"] if item["parent_id"] else 0
        if not temp.get(key, None):
            temp[key] = []
        temp[key].append(item)
    if all_categories:
        result = []
        result.extend(temp[0])
        process_childs("", result, temp)
        memory.categories = result


@categories.get("/all/", summary="WORKS: Get all categories.")
# response_model=ListOfProductsOut)
async def get_categories_all():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": memory.categories}
    )


# don't delete
"""
class CategoryPath(BaseModel):
    path: str


@categories.get("/path",
    summary='WORKS (example "stove"): Get category path (route) by its name.',
    response_model=CategoryPath)
async def get_category_path(category: str):
    category_pattern = r'^[A-Za-zА-Яа-яЁё0-9_ ]+$'
    if not fullmatch(category_pattern, category):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="INVALID_CATEGORY"
        )
    category_path = await Category.get_category_path(category=category)
    if category_path:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": category_path}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CATEGORY_NOT_FOUND"
        )
"""
