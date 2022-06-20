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
                        name=item.name,
                        age=item.age
                    )
                    for item in result
                ]
