from __future__ import annotations

from typing import cast

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000,
)


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def check_hashed_password(password: str, hashed: str) -> bool:
    return cast(bool, pwd_context.verify(password, hashed))
