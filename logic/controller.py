from db.db_connector import Database
from dotenv import load_dotenv
from logic import pwd_hashing, utils
from fastapi.responses import JSONResponse
from . import tokens
import uuid
from fastapi import HTTPException, status
from fastapi_mail import MessageSchema, FastMail
from logic.utils import *


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


async def send_email(subject, recipient, message):
    message = MessageSchema(
        subject=subject,
        recipients=recipient,
        body=message,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)
    return JSONResponse(
        status_code=200,
        content={"result": "Message has been sent"}
    )


async def reset_password(email):
    result = db.check_for_email(email)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    reset_code = str(uuid.uuid1())
    return reset_code


async def get_products_list_for_category(category, type):
    # tmp if-clause? validate it on front?
    if type not in ['bestsellers', 'new', 'rating', 'hot', 'popular']:
        return JSONResponse(
            status_code=404,
            content={"result": f"'{type} sort-type does not exist'"}
        )

    if category == 'all':
        category_id = 'p.category_id'
    else:
        category_id = db.get_category_id(category)

    if not category_id:
        return JSONResponse(
            status_code=404,
            content={"result": f"'{category}' category does not exist"}
        )
        
    result = db.get_sorted_list_of_products(type=type,
                                            category_id=category_id)
    return JSONResponse(
        status_code=200,
        content={"result": result}
    )


async def get_category_path(category):
    result = db.get_category_path(category)
    if result:
        return JSONResponse(
            status_code=200,
            content={"result": result[0]}
        )
    else:
        return JSONResponse(
            status_code=404,
            content={"result": f"'{category}' category does not exist"}
        )

