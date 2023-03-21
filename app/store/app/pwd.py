from core.security import check_hashed_password, hash_password


class PWDAccessor:
    def hash_password(self, password: str) -> str:
        return hash_password(password=password)

    def check_hashed_password(self, password: str, hashed: str) -> str:
        return check_hashed_password(password=password, hashed=hashed)
