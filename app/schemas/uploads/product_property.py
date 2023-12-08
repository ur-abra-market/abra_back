from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema


class ProductPropertyUpload(ApplicationSchema):
    matherial: Optional[List] = ""
