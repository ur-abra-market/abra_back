from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.logic.consts import *
from app.logic.queries import *
from app.orm.models import *
import app.logic.memory as memory

router = APIRouter()


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


@router.on_event("startup")
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


@router.get("/all", summary="WORKS: Get all categories.")
# response_model=ListOfProductsOut)
async def get_categories_all():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": memory.categories}
    )
