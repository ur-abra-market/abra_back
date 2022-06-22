from os import getenv
import sqlalchemy as database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, inspect, text
from db.models import *


'''
Error status codes:
1 - user not found
'''

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


    def register_user(self, user_type, first_name, last_name, phone_number, email, password):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    data = Seller(
                        first_name=first_name, 
                        last_name=last_name, 
                        phone_number=phone_number, 
                        email=email, 
                        password=password
                        )

                elif user_type == 'suppliers':
                    data = Supplier(
                        first_name=first_name, 
                        last_name=last_name, 
                        phone_number=phone_number, 
                        email=email, 
                        password=password
                        )

                elif user_type == 'admins':
                    data = Admin(
                        first_name=first_name, 
                        last_name=last_name, 
                        phone_number=phone_number, 
                        email=email, 
                        password=password
                        )

                session.add(data)
                return True


    def get_user(self, user_type, email):
        with self.session() as session:
            with session.begin():
                if user_type == 'sellers':
                    user = session\
                        .query(Seller)\
                        .filter(Seller.email.__eq__(email))\
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
                        return 1
                
                elif user_type == 'suppliers':
                    user = session\
                        .query(Supplier)\
                        .filter(Supplier.email.__eq__(email))\
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
                        return 1

                elif user_type == 'admins':
                    user = session\
                        .query(Admin)\
                        .filter(Admin.email.__eq__(email))\
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
                        return 1