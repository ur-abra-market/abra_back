from db.db_connector import Database
from dotenv import load_dotenv
from classes.enums import *
from logic import utils


load_dotenv()
db = Database()


async def get_users():
    users = db.get_users()
    return users


async def register_user(user_type, user_data):
    result = db.register_user(user_type, user_data)
    return result


async def login_user(user_type, user_data):
    db_data = db.get_password(user_type, user_data.email)
    if not db_data:
        return dict(
            response=LoginResponse.USER_NOT_FOUND,
            first_name=None
            )
    elif utils.check_hashed_password(user_data.password, db_data['password']):
        return dict(
            response=LoginResponse.OK,
            first_name=db_data['first_name']
            )
    else:
        return dict(
            response=LoginResponse.INCORRECT_PASSWORD,
            first_name=None
            )


async def update_password(user_type, user_data):
    result = db.update_password(user_type, user_data)
    return result