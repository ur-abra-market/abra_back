from __future__ import annotations

from pydantic import EmailStr


class EmailMixin:
    email: EmailStr
