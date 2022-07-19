import logging
from os import getenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from db.models import *
from classes.enums import *
from logic import utils
from sqlalchemy import text, select
from const.const import *


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


    def check_email_for_uniqueness(self, email):
        with self.session() as session:
            with session.begin():
                is_email_unique = session\
                    .query(User)\
                    .filter(User.email.__eq__(email))\
                    .scalar()
                
                if not is_email_unique:
                    return True
                else:
                    return False


    def add_user(self, user_data):
        with self.session() as session:
            with session.begin():
                current_datetime = utils.get_moscow_datetime()
                data = User(
                    first_name=user_data.first_name, 
                    last_name=user_data.last_name, 
                    email=user_data.email, 
                    phone=user_data.phone, 
                    datetime=current_datetime
                    )                     
                session.add(data)

            
    def add_password(self, user_id, password):
        with self.session() as session:
            with session.begin():
                data = UserCreds(
                    user_id=user_id,
                    password=password
                    )                 
                session.add(data)


    def get_user_id(self, email):
        with self.session() as session:
            with session.begin():
                user_id = session\
                    .query(User.id)\
                    .filter(User.email.__eq__(email))\
                    .scalar()     
                return user_id


    def add_seller(self, user_id):
        with self.session() as session:
            with session.begin():
                data = Seller(
                    user_id=user_id
                    )                     
                session.add(data)


    def add_supplier(self, user_id, additional_info):
        with self.session() as session:
            with session.begin():
                data = Supplier(
                    user_id=user_id,
                    additional_info=additional_info
                    )                     
                session.add(data)


    def get_password(self, user_id):
        with self.session() as session:
            with session.begin():
                password = session\
                    .query(UserCreds.password)\
                    .filter(UserCreds.user_id.__eq__(user_id))\
                    .scalar()
                return password


    def update_password(self, user_id, password_new):
        with self.session() as session:
            with session.begin():
                session.query(UserCreds)\
                        .where(UserCreds.user_id.__eq__(user_id))\
                        .update({UserCreds.password: password_new})


    def add_code(self, user_id, code):
        with self.session() as session:
            with session.begin():
                data = UserEmailCode(
                    user_id=user_id,
                    code=code
                )
                session.add(data)
                    

    def get_code(self, user_id):
        with self.session() as session:
            with session.begin():
                code = session\
                    .query(UserEmailCode.code)\
                    .filter(UserEmailCode.user_id.__eq__(user_id))\
                    .scalar()
                return code


    def get_category_id(self, category):
        with self.session() as session:
            with session.begin():
                category_id = session\
                    .query(Category.id)\
                    .filter(Category.name.__eq__(category))\
                    .scalar()
            return category_id


    def get_sorted_list_of_products(self, type, category_id):
        with self.engine.connect() as connection:
            if type == 'bestsellers':
                result = connection.\
                    execute(text(
                        SQL_QUERY_FOR_BESTSELLERS.format(category_id)
                    ))
            elif type == 'new':
                result = connection.\
                    execute(text(
                        SQL_QUERY_FOR_NEW_ARRIVALS.format(category_id)
                    ))
            elif type == 'rating':
                result = connection.\
                    execute(text(
                        SQL_QUERY_FOR_HIGHEST_RATINGS.format(category_id)
                    ))
            elif type == 'hot':
                result = connection.\
                    execute(text(
                        SQL_QUERY_FOR_HOT_DEALS.format(category_id)
                    ))
            elif type == 'popular':
                result = connection.\
                    execute(text(
                        SQL_QUERY_FOR_POPULAR_NOW.format(category_id)
                    ))
            return [dict(row) for row in result if result]


    def check_for_email(self, email):
        with self.session() as session:
            with session.begin():
                logging.info(email)
                result = session\
                    .query(User.email)\
                    .filter(User.email.__eq__(email))\
                    .scalar()
                logging.info(result)
                if result:
                    return True
                else:
                    return False


    def get_category_path(self, category):
        with self.engine.connect() as connection:
            result = connection.\
                    execute(text(
                        SQL_QUERY_FOR_CATEGORY_PATH.format(category)
                    ))
            return [row[0] for row in result if result]


    def create_reset_code(self, email, reset_code):
        with self.session() as session:
            with session.begin():
                data = ResetToken(
                    email=email,
                    reset_code=reset_code,
                    status="1"
                    )                     
                session.add(data)


    def check_reset_password_token(self, user_token):
        with self.session() as session:
            with session.begin():
                stmt = select(ResetToken.reset_code)\
                    .where(ResetToken.reset_code == user_token)
                result = session.execute(stmt)
                for item in result:
                    if "".join(item) == user_token:                
                        return True
                else:
                    return False
