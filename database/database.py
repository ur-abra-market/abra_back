import logging
from os import getenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from database.models import *
from classes.enums import *
from logic import utils
from sqlalchemy import text, select, delete
from logic.consts import *
import logging


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
                    email=user_data.email,
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


    def get_category_id_by_category_name(self, category):
        with self.session() as session:
            with session.begin():
                category_id = session\
                    .query(Category.id)\
                    .filter(Category.name.__eq__(category))\
                    .scalar()
            return category_id


    def get_category_id_by_product_id(self, product_id):
        with self.session() as session:
            with session.begin():
                category_id = session\
                    .query(Product.category_id)\
                    .filter(Product.id.__eq__(product_id))\
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


    # def create_reset_code(self, user_id, email, reset_code):
    #     with self.session() as session:
    #         with session.begin():
    #             data = ResetToken(
    #                 user_id=user_id,
    #                 email=email,
    #                 reset_code=reset_code,
    #                 status=True
    #                 )                     
    #             session.add(data)


    # def check_reset_password_token(self, user_token):
    #     with self.session() as session:
    #         with session.begin():
    #             stmt = select(ResetToken.reset_code)\
    #                 .where(ResetToken.reset_code == user_token)
    #             result = session.execute(stmt)
    #             for item in result:
    #                 if "".join(item) == user_token:                
    #                     return True
    #                 else:
    #                     return False


    def delete_token(self, email):
        with self.session() as session:
            with session.begin():
                stmt = delete(ResetToken)\
                    .where(ResetToken.email == email)
                session.execute(stmt)


    def get_similar_products(self, product_id):
        with self.engine.connect() as connection:
            result = connection.\
                    execute(
                        SQL_QUERY_FOR_SIMILAR_PRODUCTS, {'product_id': product_id}
                    )
            return [dict(row) for row in result if result]


    def get_images_by_product_id(self, product_id):
        with self.session() as session:
            with session.begin():
                result = session\
                    .query(ProductImage.image_url, ProductImage.serial_number)\
                    .filter(ProductImage.product_id.__eq__(product_id))\
                    .all()
                return [dict(image_url=row[0], serial_number=row[1]) for row in result if result]


    def get_latest_searches_by_user_id(self, user_id):
        with self.session() as session:
            with session.begin():
                result =  session\
                    .query(UserSearch.search_query, UserSearch.datetime)\
                    .filter(UserSearch.user_id.__eq__(user_id))\
                    .all()
                return [dict(search_query=row[0], datetime=str(row[1])) for row in result if result]