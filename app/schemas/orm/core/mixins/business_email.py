from __future__ import annotations

from typing import Optional

from pydantic import EmailStr


class BusinessEmailMixin:
    business_email: Optional[EmailStr] = None
