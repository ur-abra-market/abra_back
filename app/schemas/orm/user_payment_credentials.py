from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class UserPaymentCredentials(ORMSchema):
    user_id: int
    card_holder: str
    card_number: str
    expired_date: str
