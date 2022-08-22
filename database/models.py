from dataclasses import dataclass
from decimal import Decimal
from email.policy import default
from sqlalchemy import select, Column, Integer, String, ForeignKey, Boolean, DateTime, SmallInteger, Text, DECIMAL, text, func
from sqlalchemy.orm import declarative_base, relationship
from .init import async_session
from logic.consts import *


Base = declarative_base()


class UserMixin:
    @classmethod
    async def get_user_id(cls, email):
        async with async_session() as session:
            user_id = await session.\
                execute(select(cls.id).where(cls.email.__eq__(email)))
            return user_id.scalar()


class CategoryMixin:
    @classmethod
    async def get_category_id(cls, category_name):
        async with async_session() as session:
            category_id = await session.\
                execute(select(cls.id).where(cls.name.__eq__(category_name)))
            return category_id.scalar()

    @classmethod
    async def get_category_path(cls, category):
        async with async_session() as session:
            category_path = await session\
                .execute(QUERY_FOR_CATEGORY_PATH.format(category))
            return category_path.scalar()


class ProductGradeMixin:
    @classmethod
    async def get_product_grade(cls, product_id):
        async with async_session() as session:
            grade = await session\
                .execute(QUERY_FOR_PRODUCT_GRADE.format(product_id))
            for row in grade:  # grade always consists of 1 row
                result = dict(grade_average=row[0],
                              count_all=row[1])
            return result

    @classmethod
    async def get_product_grade_details(cls, product_id):
        async with async_session() as session:
            result = await session\
                .execute(QUERY_FOR_PRODUCT_GRADE_DETAILS.format(product_id))
            result = [dict(grade=row[0],
                           count=row[1]
                           ) for row in result if result]
            for grade_value in range(1, 6):
                if grade_value not in [row['grade'] for row in result]:
                    result.append(dict(grade=grade_value, count=0))
            return result

    @classmethod
    async def is_product_exist(cls, product_id):
        async with async_session() as session:
            is_exist = await session\
                .execute(select(cls.id)\
                .where(cls.id.__eq__(product_id)))
            is_exist = bool(is_exist.scalar())
            return is_exist


class SupplierMixin:
    @classmethod
    async def get_supplier_info(cls, product_id):
        async with async_session() as session:
            supplier = await session\
                .execute(text(QUERY_FOR_SUPPLIER_INFO.format(product_id)))
            return [dict(row) for row in supplier if supplier]


class ProductImageMixin:
    @classmethod
    async def get_images(cls, product_id):
        async with async_session() as session:
            images = await session\
                .execute(select(cls.image_url, cls.serial_number)\
                .where(cls.product_id.__eq__(product_id)))
            return [dict(row) for row in images if images]


@dataclass
class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    email = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    datetime = Column(DateTime, nullable=False)
    is_supplier = Column(Boolean, nullable=False)

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
class Supplier(Base, SupplierMixin):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_name = Column(String(50), nullable=True)
    grade_average = Column(DECIMAL(2,1), nullable=False, default=0)
    count = Column(Integer, nullable=False, default=0)
    license_number = Column(Integer, nullable=False)
    additional_info = Column(Text, nullable=True)


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
class Product(Base, ProductGradeMixin):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    with_discount = Column(Boolean, nullable=True)
    count = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    grade_average = Column(DECIMAL(2,1), nullable=False, default=0)


@dataclass
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_number = Column(Integer, nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)
    is_completed = Column(Integer, nullable=False)


@dataclass
class Category(Base, CategoryMixin):
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
    grade_overall = Column(Integer, nullable=False)
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
class ProductImage(Base, ProductImageMixin):
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
    value = Column(DECIMAL(9,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    discount = Column(DECIMAL(3,2), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False)


@dataclass
class UserSearch(Base):
    __tablename__ = "user_searches"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_query = Column(Text, nullable=False)
    datetime = Column(DateTime, nullable=False)


@dataclass
class CategoryProperty(Base):
    __tablename__ = "category_properties"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    property_type_id = Column(Integer, ForeignKey("category_property_types.id"), nullable=False)


@dataclass
class CategoryPropertyType(Base):
    __tablename__ = "category_property_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)


@dataclass
class CategoryPropertyValue(Base):
    __tablename__ = "category_property_values"
    id = Column(Integer, primary_key=True)
    property_type_id = Column(Integer, ForeignKey("category_property_types.id"), nullable=False)
    value = Column(String(50), nullable=False)


@dataclass
class CategoryVariationType(Base):
    __tablename__ = "category_variation_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)


@dataclass
class CategoryVariationValue(Base):
    __tablename__ = "category_variation_values"
    id = Column(Integer, primary_key=True)
    variation_type_id = Column(Integer, ForeignKey("category_variation_types.id"), nullable=False)
    value = Column(String(50), nullable=False)


@dataclass
class CategoryVariation(Base):
    __tablename__ = "category_variations"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    variation_type_id = Column(Integer, ForeignKey("category_variation_types.id"), nullable=False)


@dataclass
class ProductPropertyValue(Base):
    __tablename__ = "product_property_values"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    property_value_id = Column(Integer, ForeignKey("category_property_values.id"), nullable=False)


@dataclass
class ProductVariationValue(Base):
    __tablename__ = "product_variation_values"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variation_value_id = Column(Integer, ForeignKey("category_variation_values.id"), nullable=False)


@dataclass
class SellerFavorite(Base):
    __tablename__ = "seller_favorites"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)


@dataclass
class UserAdress(Base):
    __tablename__="user_adresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    country = Column(String(30), nullable=False)
    area = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    street = Column(String(100), nullable=False)
    building = Column(String(20), nullable=False)
    appartment = Column(String(20), nullable=False)
    postal_code = Column(String(20), nullable=False)
