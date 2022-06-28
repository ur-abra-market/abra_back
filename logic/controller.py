from db.db_connector import Database
from dotenv import load_dotenv
from classes.enums import *
from logic import utils
from fastapi.responses import JSONResponse


load_dotenv()
db = Database()


async def get_users():
    users = db.get_users()
    return users


async def register_user(user_type, user_data):
    is_email_unique = db.check_email_for_uniqueness(user_type=user_type,
                                                    email=user_data.email)
    if is_email_unique:
        user_data.password = utils.hash_password(password=user_data.password)
        db.register_user(user_type=user_type, user_data=user_data)
        return dict(
                result='Registration successfull!'
            )
    else:
        return JSONResponse(
                status_code=404,
                content={"result": "User with this email already exists"}
            )


async def login_user(user_type, user_data):
    if user_type not in ['sellers', 'suppliers']:
        return JSONResponse(
                status_code=404,
                content={"result": "Incorrect subdomain"}
            )

    hashed_password_db = db.get_password(user_type=user_type,
                                         email=user_data.email)
    is_passwords_match = utils.check_hashed_password(password=user_data.password,
                                                     hashed=hashed_password_db)
    if hashed_password_db and is_passwords_match:
        return dict(
            result='Login successfull!'
        )
    else:
        return JSONResponse(
                status_code=404,
                content={"result": "Login failed"}
            )


async def update_password(user_type, user_data):
    if user_type not in ['sellers', 'suppliers']:
        return JSONResponse(
                status_code=404,
                content={"result": "Incorrect subdomain"}
            )

    hashed_password_db = db.get_password(user_type=user_type,
                                         email=user_data.email)
    is_passwords_match = utils.check_hashed_password(password=user_data.old_password,
                                                     hashed=hashed_password_db)
    if hashed_password_db and is_passwords_match:
        hashed_password_new = utils.hash_password(password=user_data.new_password)
        db.update_password(user_type=user_type,
                           email=user_data.email,
                           password_new=hashed_password_new)
        # check: Has the password been updated?
        return dict(
                result='Password changed successfully!'
            )
    else:
        return JSONResponse(
                status_code=404,
                content={"result": "Wrong credentials"}
            )