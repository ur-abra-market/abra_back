from db.db_connector import Database
from dotenv import load_dotenv
from classes.enums import *
from logic import utils
from fastapi.responses import JSONResponse


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
    hashed_password = utils.hash_password(password=user_data.password)
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
    user_id = db.get_user_id(email=user_data.email)
    if not user_id:
        return JSONResponse(
                status_code=404,
                content={"result": "Wrong credentials"}
            )
    hashed_password_from_db = db.get_password(user_id=user_id)
    is_passwords_match = utils.check_hashed_password(password=user_data.password,
                                                     hashed=hashed_password_from_db)
    if hashed_password_from_db and is_passwords_match:
        return JSONResponse(
                status_code=200,
                content={"result": "Login successfull!"}
            )
    else:
        return JSONResponse(
                status_code=404,
                content={"result": "Wrong credentials"}
            )


async def change_password(user_data):
    user_id = db.get_user_id(email=user_data.email)
    hashed_password_db = db.get_password(user_id=user_id)
    is_passwords_match = utils.check_hashed_password(password=user_data.old_password,
                                                     hashed=hashed_password_db)
    if hashed_password_db and is_passwords_match:
        hashed_password_new = utils.hash_password(password=user_data.new_password)
        db.update_password(user_id=user_id,
                           password_new=hashed_password_new)
        # check: Has the password been updated?
        return JSONResponse(
                status_code=200,
                content={"result": "Password changed successfully!"}
            )
    else:
        return JSONResponse(
                status_code=404,
                content={"result": "Wrong credentials"}
            )