from os import getenv
import sqlalchemy as database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, inspect, text
from db.models import *


class Database:
    def __init__(self):
        db_credentials = "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}".format(
            user=getenv('RDS_USERNAME'),
            password=getenv('RDS_PASSWORD'),
            host=getenv('RDS_HOSTNAME'),
            port=getenv('RDS_PORT'),
            db_name=getenv('RDS_DB_NAME')
        )
        self.engine = database.create_engine(db_credentials)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def get_users(self):
        with self.session() as session:
            with session.begin():
                result = session\
                    .query(User)\
                    .all()

                return [
                    dict(
                        id=item.id,
                        first_name=item.first_name,
                        last_name=item.last_name,
                        phone_number=item.phone_number,
                        email=item.email
                    )
                    for item in result
                ]

    def register_user(self, first_name, last_name, phone_number, email, password):
        with self.session() as session:
            with session.begin():
                data = User(
                    first_name=first_name, 
                    last_name=last_name, 
                    phone_number=phone_number, 
                    email=email, 
                    password=password
                    )
                session.add(data)
            return True

    def get_user(self, email):
        with self.session() as session:
            with session.begin():
                user = session\
                    .query(User)\
                    .filter(User.email.__eq__(email))\
                    .scalar()
                if user:
                    return dict(
                            id=user.id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            phone_number=user.phone_number,
                            email=user.email,
                            password=user.password
                        )
                else:
                    return None