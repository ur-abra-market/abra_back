from db.db_connector import Database
from dotenv import load_dotenv


'''
Error status codes:
1 - user not found
2 - incorrect password
'''


load_dotenv()
db = Database()


async def get_users():
    users = db.get_users()
    return users


async def register_user(user_type, first_name, last_name, phone_number, email, password):
    result = db.register_user(user_type, first_name, last_name, phone_number, email, password)
    return result


async def login_user(user_type, email, password):
    user = db.get_user(user_type, email)
    if user == 1:
        return 1
    elif user['password'] == password:
        username = dict(
            first_name=user['first_name'],
            last_name=user['last_name']
        )
        return username
    else:
        return 2
