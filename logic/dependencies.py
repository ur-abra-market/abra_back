from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import utils
from . import tokens
from classes.response_models import *
from . import controller as c
from jose import jwt
import jose
from pydantic import ValidationError


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> MyEmail:
    try:
        token_data = jwt.decode(
            token, tokens.JWT_SECRET_KEY, algorithms=[tokens.ALGORITHM]
        )

    except(jose.exceptions.ExpiredSignatureError):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except(jose.exceptions.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = dict(email=token_data['sub'])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return MyEmail(**user)