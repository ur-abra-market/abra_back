from __future__ import annotations

from core.security import check_hashed_password, hash_password


class PWDAccessor:
    def __init__(self) -> None:
        self.check_hashed_password = check_hashed_password
        self.hash_password = hash_password
