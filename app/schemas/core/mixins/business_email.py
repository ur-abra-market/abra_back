from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from utils.pydantic import EmailStr


class BusinessEmailMixin(BaseModel):
    business_email: Optional[EmailStr] = None
