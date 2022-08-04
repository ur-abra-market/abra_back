from dataclasses import dataclass
from sqlalchemy import select, Column, Integer, String, ForeignKey, Boolean, DateTime, SmallInteger, Text, DECIMAL
from sqlalchemy.orm import declarative_base, relationship
from .init import async_session


Base = declarative_base()


class MixinGetBy:
    @classmethod
    async def get_user_id(cls, email):
        async with async_session() as session:
            user_id = await session.\
                execute(select(cls.id).where(cls.email.__eq__(email)))
            return user_id.scalar()


@dataclass
class User(Base, MixinGetBy):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    email = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    datetime = Column(DateTime, nullable=False)

    creds = relationship("UserCreds", back_populates="user")


@dataclass
class UserCreds(Base):
    __tablename__ = "user_creds"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    password = Column(Text, nullable=False)

    user = relationship("User", back_populates="creds")


@dataclass
class UserImage(Base):
    __tablename__ = "user_images"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thumbnail_url = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)


@dataclass
class Seller(Base):
    __tablename__ = "sellers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


@dataclass
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


@dataclass
class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


@dataclass
class ResetToken(Base):
    __tablename__ = "reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(50), nullable=False)
    reset_code = Column(String(50), nullable=False)
    status = Column(Boolean, nullable=False)


@dataclass
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    with_discount = Column(Boolean, nullable=True)
    count = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)


@dataclass
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)
    is_completed = Column(Integer, nullable=False)


@dataclass
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, nullable=True)


@dataclass
class ProductReview(Base):
    __tablename__ = "product_reviews"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    text = Column(Text, nullable=False)
    grade_overall = Column(DECIMAL, nullable=False)
    datetime = Column(DateTime, nullable=False)


@dataclass
class ProductReviewReaction(Base):
    __tablename__ = "product_review_reactions"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_review_id = Column(Integer, ForeignKey("product_reviews.id"), nullable=False)
    reaction = Column(Boolean, nullable=False)


@dataclass
class ProductReviewPhoto(Base):
    __tablename__ = "product_review_photos"
    id = Column(Integer, primary_key=True)
    product_review_id = Column(Integer, ForeignKey("product_reviews.id"), nullable=False)
    image_url = Column(Text, nullable=False)


@dataclass
class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(Text, nullable=False)
    serial_number = Column(Integer, nullable=False)


@dataclass
class ProductPrice(Base):
    __tablename__ = "product_prices"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    value = Column(DECIMAL, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(DECIMAL, nullable=True)
    datetime = Column(DateTime, nullable=False)


@dataclass
class UserSearch(Base):
    __tablename__ = "user_searches"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_query = Column(Text, nullable=False)
    datetime = Column(DateTime, nullable=False)
