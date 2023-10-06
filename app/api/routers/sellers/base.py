from fastapi import APIRouter
from fastapi.param_functions import Depends

from core.depends import seller

router = APIRouter(dependencies=[Depends(seller)])
