from db.db_connector import Database
from dotenv import load_dotenv


load_dotenv()
db = Database()


async def get_users():
    users = db.get_users()
    return users


async def register_user(first_name, last_name, phone_number, email, password):
    result = db.register_user(first_name, last_name, phone_number, email, password)
    return result


async def login_user(email, password):
    user = db.get_user(email)
    if user['password'] == password:
        username = dict(
            first_name=user['first_name'],
            last_name=user['last_name']
        )
        return username
    else:
        return False
