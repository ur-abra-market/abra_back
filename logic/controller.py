from db.db_connector import Database


from dotenv import load_dotenv
load_dotenv()

db = Database()


async def get_users():
    users = db.get_users()
    return users
