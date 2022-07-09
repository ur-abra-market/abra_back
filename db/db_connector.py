from os import getenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from db.models import *
from classes.enums import *
from logic import utils


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
