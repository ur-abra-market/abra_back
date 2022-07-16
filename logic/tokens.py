# from typing import Union, Any
# from jose import jwt
# from datetime import timedelta
# from os import getenv
# from . import utils


# ACCESS_TOKEN_EXPIRE_MINUTES = 60
# REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
# ALGORITHM = "HS256"
# JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
# JWT_REFRESH_SECRET_KEY = getenv('JWT_REFRESH_SECRET_KEY')


# def create_access_token(subject: Union[str, Any]) -> str:
#     expires_delta = utils.get_moscow_datetime() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode = dict(
#         exp=expires_delta, 
#         sub=str(subject)
#     )
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
#     return encoded_jwt

# # refresh_token isn't use yet
# def create_refresh_token(subject: Union[str, Any]) -> str:
#     expires_delta = utils.get_moscow_datetime() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
#     to_encode = dict(
#         exp=expires_delta, 
#         sub=str(subject)
#     )
#     encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
#     return encoded_jwt

