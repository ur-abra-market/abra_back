from db.db_connector import Database
from dotenv import load_dotenv
from logic import pwd_hashing, utils
from fastapi.responses import JSONResponse
from . import tokens
import uuid
from fastapi import HTTPException, status


load_dotenv()
db = Database()


async def register_user(user_type, user_data):
    if user_type not in ['sellers', 'suppliers']:
        return JSONResponse(
            status_code=404,
            content={"result": "Incorrect subdomain"}
        )
    is_email_unique = db.check_email_for_uniqueness(email=user_data.email)
    if not is_email_unique:
        return JSONResponse(
            status_code=404,
            content={"result": "User with this email already exists"}
        )
    db.add_user(user_data=user_data)
    user_id = db.get_user_id(email=user_data.email)
    hashed_password = pwd_hashing.hash_password(password=user_data.password)
    db.add_password(user_id=user_id, password=hashed_password)
    if user_type == 'sellers':
        db.add_seller(user_id=user_id)
    elif user_type == 'suppliers':
        db.add_supplier(user_id=user_id,
                        additional_info=user_data.additional_info)
    return JSONResponse(
        status_code=200,
        content={"result": "Registration successfull!"}
    )


async def login_user(user_data):
    user_id = db.get_user_id(email=user_data.username)
    if not user_id:
        return JSONResponse(
            status_code=404,
            content={"result": "Wrong credentials"}
        )
    hashed_password_from_db = db.get_password(user_id=user_id)
    is_passwords_match = pwd_hashing.check_hashed_password(password=user_data.password,
                                                     hashed=hashed_password_from_db)
    if hashed_password_from_db and is_passwords_match:
        access_token = tokens.create_access_token(subject=user_data.username)
        refresh_token = tokens.create_refresh_token(subject=user_data.username)
        return JSONResponse(
            status_code=200,
            content=dict(
                access_token=access_token,
                refresh_token=refresh_token
            )
        )
    else:
        return JSONResponse(
            status_code=404,
            content={"result": "Wrong credentials"}
        )


async def change_password(user_data, user_email):
    user_id = db.get_user_id(email=user_email)
    hashed_password_db = db.get_password(user_id=user_id)
    is_passwords_match = \
        pwd_hashing.check_hashed_password(password=user_data.old_password,
                                          hashed=hashed_password_db)
    if hashed_password_db and is_passwords_match:
        hashed_password_new = \
            pwd_hashing.hash_password(password=user_data.new_password)
        db.update_password(user_id=user_id,
                           password_new=hashed_password_new)
        return JSONResponse(
            status_code=200,
            content={"result": "Password changed successfully!"}
        )
    else:
        return JSONResponse(
            status_code=404,
            content={"result": f"Wrong credentials"}
        )


async def get_code(email):
    code = utils.get_rand_code
    user_id = db.get_user_id(email=email)
    db.add_code(user_id, code)
    return code


async def check_confirm_code(email, code):
    user_id = db.get_user_id(email=email)
    code_from_db = db.get_code(user_id=user_id)
    if code_from_db == code:
        return JSONResponse(
            status_code=200,
            content={"result": "Sucсessful registration"}
        )
    else:
        return JSONResponse(
            status_code=404,
            content={"result": "Check your code and try again"}
        )


async def get_token(user_id):
    token = db.get_token(user_id=user_id)
    return token


async def reset_password(email):
    result = db.check_email_for_uniqueness(email)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    reset_code = str(uuid.uuid1())
    return reset_code