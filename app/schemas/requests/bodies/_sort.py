from typing import Optional

from pydantic import BaseModel

from enums import SortType


class Sort(BaseModel):
    category_id: Optional[int] = None
    sort_type: SortType = SortType.RATING
    ascending: bool = False
