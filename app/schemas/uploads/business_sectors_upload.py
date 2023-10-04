from __future__ import annotations

from typing import List

from utils.pydantic import BaseJSONSchema

from ..schema import ApplicationSchema


class BusinessSectorsUpload(BaseJSONSchema, ApplicationSchema):
    business_sectors: List[int]
