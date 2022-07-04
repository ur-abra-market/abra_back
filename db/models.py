from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, DateTime, SmallInteger
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)


class UserCreds(Base):
    __tablename__ = "user_creds"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)


class UserImage(Base):
    __tablename__ = "user_images"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thumbnail_url = Column(String, nullable=False)
    source_url = Column(String, nullable=False)


class Seller(Base):
    __tablename__ = "sellers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    additional_info = Column(String, nullable=True)


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class User_email_codes(Base):
    __tablename__ = "user_email_codes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(SmallInteger, nullable=False )
