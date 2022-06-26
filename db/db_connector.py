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
                # bad approach?
                # if user_type == 'sellers':
                #     class UserType(Seller):
                #         pass
                hashed_password = utils.hash_password(user_data.password)
                if user_type == 'sellers':
                    data = Seller(
                        first_name=user_data.first_name, 
                        last_name=user_data.last_name, 
                        phone_number=user_data.phone_number, 
                        email=user_data.email, 
                        password=hashed_password
                        )                     

                elif user_type == 'suppliers':
                    data = Supplier(
                        first_name=user_data.first_name, 
                        last_name=user_data.last_name, 
                        phone_number=user_data.phone_number, 
                        email=user_data.email, 
                        password=hashed_password
                        )

                elif user_type == 'admins':
                    data = Admin(
                        first_name=user_data.first_name, 
                        last_name=user_data.last_name, 
                        phone_number=user_data.phone_number, 
                        email=user_data.email, 
                        password=hashed_password
                        )

                try:
                    session.add(data)
                    session.flush()  # workaround for try-except to work
                    return RegisterResponse.OK
                except sqlalchemy.exc.IntegrityError:
                    return RegisterResponse.EMAIL_ALREADY_EXIST
                except sqlalchemy.exc.DataError:
                    return RegisterResponse.WRONG_DATA


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
                return None


    def update_password(self, user_type, user_data):
        with self.session() as session:
            with session.begin():
                hashed_new_password = utils.hash_password(user_data.new_password)
                if user_type == 'sellers':
                    password = session\
                            .query(Seller.password)\
                            .filter(Seller.email.__eq__(user_data.email))\
                            .scalar()
                    if not password:
                        return PasswordUpdatingResponse.USER_NOT_FOUND
                    elif utils.check_hashed_password(user_data.old_password, password):
                        session.query(Seller)\
                                .where(Seller.email.__eq__(user_data.email))\
                                .update({Seller.password: hashed_new_password})
                        return PasswordUpdatingResponse.OK
                    else:
                        return PasswordUpdatingResponse.INCORRECT_PASSWORD

                elif user_type == 'suppliers':
                    password = session\
                            .query(Supplier.password)\
                            .filter(Supplier.email.__eq__(user_data.email))\
                            .scalar()
                    if not password:
                        return PasswordUpdatingResponse.USER_NOT_FOUND
                    elif utils.check_hashed_password(user_data.old_password, password):
                        session.query(Supplier)\
                                .where(Supplier.email.__eq__(user_data.email))\
                                .update({Supplier.password: hashed_new_password})
                        return PasswordUpdatingResponse.OK
                    else:
                        return PasswordUpdatingResponse.INCORRECT_PASSWORD

                elif user_type == 'admins':
                    password = session\
                            .query(Admin.password)\
                            .filter(Admin.email.__eq__(user_data.email))\
                            .scalar()
                    if not password:
                        return PasswordUpdatingResponse.USER_NOT_FOUND
                    elif utils.check_hashed_password(user_data.old_password, password):
                        session.query(Admin)\
                                .where(Admin.email.__eq__(user_data.email))\
                                .update({Admin.password: hashed_new_password})
                        return PasswordUpdatingResponse.OK
                    else:
                        return PasswordUpdatingResponse.INCORRECT_PASSWORD
