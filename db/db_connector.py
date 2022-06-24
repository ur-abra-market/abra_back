from os import getenv
import sqlalchemy as database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, inspect, text
from db.models import *
from classes.enums import *


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

    def get_users(self, user_type):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    result = session\
                        .query(Seller)\
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

                elif user_type == 'suppliers':
                    result = session\
                        .query(Supplier)\
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

                elif user_type == 'admins':
                    result = session\
                        .query(Admin)\
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


    def register_user(self, user_type, user_data):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    data = Seller(
                        first_name=user_data.first_name, 
                        last_name=user_data.last_name, 
                        phone_number=user_data.phone_number, 
                        email=user_data.email, 
                        password=user_data.password
                        )

                elif user_type == 'suppliers':
                    data = Supplier(
                        first_name=user_data.first_name, 
                        last_name=user_data.last_name, 
                        phone_number=user_data.phone_number, 
                        email=user_data.email, 
                        password=user_data.password
                        )

                elif user_type == 'admins':
                    data = Admin(
                        first_name=user_data.first_name, 
                        last_name=user_data.last_name, 
                        phone_number=user_data.phone_number, 
                        email=user_data.email, 
                        password=user_data.password
                        )
                else:
                    return RegisterResponse.INCORRECT_USER_TYPE

                session.add(data)
                return RegisterResponse.OK


    def get_password(self, user_type, email):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    user_data = session\
                        .query(Seller)\
                        .filter(Seller.email.__eq__(email))\
                        .scalar()
                    if user_data:
                        return dict(
                            password=user_data.password,
                            first_name=user_data.first_name
                        )
                
                elif user_type == 'suppliers':
                    user_data = session\
                        .query(Supplier)\
                        .filter(Supplier.email.__eq__(email))\
                        .scalar()
                    if user_data:
                        return dict(
                            password=user_data.password,
                            first_name=user_data.first_name
                        )

                elif user_type == 'admins':
                    user_data = session\
                        .query(Admin)\
                        .filter(Admin.email.__eq__(email))\
                        .scalar()
                    if user_data:
                        return dict(
                            password=user_data.password,
                            first_name=user_data.first_name
                        )
                    return False


    def update_password(self, email, old_password, new_password):
        # possible logic for creating password during registration:
        # old_password = null and password (in db) = null, as result password updated (created)
        with self.session() as session:
            with session.begin():
                password = session\
                        .query(Seller)\
                        .filter(Seller.email.__eq__(email))\
                        .scalar()
                if password == old_password:
                    session.query(Seller)\
                            .where(Seller.email.__eq__(email))\
                            .update({Seller.password: new_password})
                    return True
                else:
                    return 2