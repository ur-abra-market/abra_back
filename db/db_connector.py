from os import getenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from db.models import *
from classes.enums import *
from logic import utils
import pymysql


class Database:
    def __init__(self):
        db_credentials = "mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}".format(
            user=getenv('RDS_USERNAME'),
            password=getenv('RDS_PASSWORD'),
            host=getenv('RDS_HOSTNAME'),
            port=getenv('RDS_PORT'),
            db_name=getenv('RDS_DB_NAME')
        )
        self.engine = sqlalchemy.create_engine(db_credentials)
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


    def check_email_for_uniqueness(self, user_type, email):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    is_email_unique = session\
                        .query(Seller)\
                        .filter(Seller.email.__eq__(email))\
                        .scalar()
                elif user_type == 'suppliers':
                    is_email_unique = session\
                        .query(Supplier)\
                        .filter(Supplier.email.__eq__(email))\
                        .scalar()
                
                if not is_email_unique:
                    return True
                else:
                    return False
                

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

                session.add(data)


    def get_password(self, user_type, email):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    password_db = session\
                        .query(Seller.password)\
                        .filter(Seller.email.__eq__(email))\
                        .scalar()
                
                elif user_type == 'suppliers':
                    password_db = session\
                        .query(Supplier.password)\
                        .filter(Supplier.email.__eq__(email))\
                        .scalar()
                        
                return password_db


    def update_password(self, user_type, email, password_new):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    session.query(Seller)\
                            .where(Seller.email.__eq__(email))\
                            .update({Seller.password: password_new})

                elif user_type == 'suppliers':
                    session.query(Supplier)\
                            .where(Supplier.email.__eq__(email))\
                            .update({Supplier.password: password_new})