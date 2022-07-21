from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, DateTime, SmallInteger, VARCHAR, TIMESTAMP, Text, DECIMAL
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    datetime = Column(DateTime, nullable=False)


class UserCreds(Base):
    __tablename__ = "user_creds"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    password = Column(String, nullable=False)


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


class ResetToken(Base):
    __tablename__ = "reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String, nullable=False)
    reset_code = Column(String, nullable=False)
    status = Column(String, nullable=False)


class UserEmailCode(Base):
    __tablename__ = "user_email_codes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(SmallInteger, nullable=False)
    

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    with_discount = Column(Boolean, nullable=True)
    datetime = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)
    is_completed = Column(Integer, nullable=False)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, ForeignKey("products.category_id"), primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, nullable=True)


class ProductReview(Base):
    __tablename__ = "product_reviews"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    text = Column(Text, nullable=False)
    grade_overall = Column(DECIMAL, nullable=False)
    datetime = Column(DateTime, nullable=False)


class ProductReviewReaction(Base):
    __tablename__ = "product_review_reactions"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_review_id = Column(Integer, ForeignKey("product_reviews.id"), nullable=False)
    reaction = Column(Boolean, nullable=False)


class ProductReviewPhoto(Base):
    __tablename__ = "product_review_photos"
    id = Column(Integer, primary_key=True)
    product_review_id = Column(Integer, ForeignKey("product_reviews.id"), nullable=False)
    image_url = Column(Text, nullable=False)


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    image_url = Column(Text, nullable=False)


class ProductPrice(Base):
    __tablename__ = "product_prices"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    value = Column(DECIMAL, nullable=False)
    discount = Column(DECIMAL, nullable=True)
    datetime = Column(DateTime, nullable=False)
