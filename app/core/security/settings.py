from pydantic import BaseModel

from ..settings import jwt_settings


class Settings(BaseModel):
    authjwt_secret_key: str = jwt_settings.JWT_SECRET_KEY
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = jwt_settings.COOKIE_SECURE
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = False
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    authjwt_cookie_samesite: str = jwt_settings.COOKIE_SAMESITE
    authjwt_cookie_domain = jwt_settings.COOKIE_DOMAIN
    authjwt_cookie_max_age: int = 86400
