import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette import status

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_google_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        google_user_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return google_user_info
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
            headers={"WWW-Authenticate": "JWT"},
        )
