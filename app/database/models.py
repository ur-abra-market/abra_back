from dataclasses import dataclass
from sqlalchemy import (
    select,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    Text,
    DECIMAL,
    text,
    and_,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from .init import async_session
from app.logic.consts import *
from app.logic.utils import get_moscow_datetime
from typing import Optional
import datetime


Base = declarative_base()


class UserMixin:
    @classmethod
    async def get_user_id(cls, email):
        async with async_session() as session:
            user_id = await session.execute(
                select(cls.id).where(cls.email.__eq__(email))
            )
            return user_id.scalar()

    @classmethod
    async def get_user_role(cls, email):
        async with async_session() as session:
            user_id = await session.execute(
                select(cls.is_supplier).where(cls.email.__eq__(email))
            )
            return user_id.scalar()


class CategoryMixin:
    @classmethod
    async def get_category_id(cls, category_name):
        async with async_session() as session:
            category_id = await session.execute(
                select(cls.id).where(cls.name.__eq__(category_name))
            )
            return category_id.scalar()

    @classmethod
    async def get_category_path(cls, category):
        async with async_session() as session:
            category_path = await session.execute(
                QUERY_FOR_CATEGORY_PATH.format(category)
            )
            return category_path.scalar()

    @classmethod
    async def get_all_categories(cls):
        async with async_session() as session:
            all_categories = await session.execute(QUERY_ALL_CATEGORIES)
            all_categories = [dict(row) for row in all_categories if all_categories]
            return all_categories

    @classmethod
    async def is_category_id_exist(cls, category_id):
        async with async_session() as session:
            category_id = await session.execute(
                select(cls.id).where(cls.id.__eq__(category_id))
            )
            return bool(category_id.scalar())


class ProductMixin:
    @classmethod
    async def get_product_grade(cls, product_id):
        async with async_session() as session:
            grade = await session.execute(QUERY_FOR_PRODUCT_GRADE.format(product_id))
            for row in grade:
                result = dict(row)
            return result

    @classmethod
    async def get_product_grade_details(cls, product_id):
        async with async_session() as session:
            result = await session.execute(
                QUERY_FOR_PRODUCT_GRADE_DETAILS.format(product_id)
            )
            result = [dict(grade=row[0], count=row[1]) for row in result if result]
            for grade_value in range(1, 6):
                if grade_value not in [row["grade"] for row in result]:
                    result.append(dict(grade=grade_value, count=0))
            return result

    @classmethod
    async def is_product_exist(cls, product_id):
        async with async_session() as session:
            is_exist = await session.execute(
                select(cls.id).where(cls.id.__eq__(product_id))
            )
            return bool(is_exist.scalar())

    @classmethod
    async def get_category_id(cls, product_id):
        async with async_session() as session:
            category_id = await session.execute(
                select(cls.category_id).where(cls.id.__eq__(product_id))
            )
            return category_id.scalar()

    @classmethod
    async def is_product_match_supplier(cls, product_id, supplier_id):
        async with async_session() as session:
            is_match = await session.execute(
                select(cls.id).where(
                    and_(cls.id.__eq__(product_id), cls.supplier_id.__eq__(supplier_id))
                )
            )
            return bool(is_match.scalar())

    @classmethod
    async def is_product_active(cls, product_id):
        async with async_session() as session:
            is_active = await session.execute(
                select(cls.is_active).where(and_(cls.id.__eq__(product_id)))
            )
            return bool(is_active.scalar())


class SupplierMixin:
    @classmethod
    async def get_supplier_info(cls, product_id):
        async with async_session() as session:
            supplier = await session.execute(
                text(QUERY_FOR_SUPPLIER_INFO.format(product_id=product_id))
            )
            result = None
            for row in supplier:
                result = dict(row)
            return result

    @classmethod
    async def is_supplier_exist(cls, supplier_id):
        async with async_session() as session:
            is_exist = await session.execute(
                select(cls.id).where(cls.id.__eq__(supplier_id))
            )
            is_exist = bool(is_exist.scalar())
            return is_exist

    @classmethod
    async def get_supplier_id(cls, user_id):
        async with async_session() as session:
            supplier_id = await session.execute(
                select(cls.id).where(cls.user_id.__eq__(user_id))
            )
            return supplier_id.scalar()

    @classmethod
    async def get_supplier_id_by_email(cls, email):
        async with async_session() as session:
            supplier_id = await session.execute(
                select(cls.id).join(User).where(User.email.__eq__(email))
            )
            return supplier_id.scalar()


class ProductImageMixin:
    @classmethod
    async def get_images(cls, product_id):
        async with async_session() as session:
            images = await session.execute(
                select(cls.image_url, cls.serial_number).where(
                    cls.product_id.__eq__(product_id)
                )
            )
            return [dict(row) for row in images if images]


# works for both category_property_types and category_variation_types
class CategoryPVTypeMixin:
    @classmethod
    async def get_id(cls, name):
        async with async_session() as session:
            id = await session.execute(select(cls.id).where(cls.name.__eq__(name)))
            return id.scalar()


class SellerMixin:
    @classmethod
    async def get_seller_id(cls, user_id):
        async with async_session() as session:
            seller_id = await session.execute(
                select(cls.id).where(cls.user_id.__eq__(user_id))
            )
            return seller_id.scalar()

    @classmethod
    async def get_seller_id_by_email(cls, email):
        async with async_session() as session:
            seller_id = await session.execute(
                select(cls.id).join(User).where(User.email.__eq__(email))
            )
            return seller_id.scalar()


class ProductVariationValueMixin:
    @classmethod
    async def get_product_variation_value_id(
        cls, product_id, category_variation_value_id
    ):
        async with async_session() as session:
            product_variation_value_id = await session.execute(
                select(cls.id).where(
                    and_(
                        cls.product_id.__eq__(product_id),
                        cls.variation_value_id.__eq__(category_variation_value_id),
                    )
                )
            )
            return product_variation_value_id.scalar()


class CategoryPropertyValueMixin:
    @classmethod
    async def get_category_property_value_id(
        cls, category_property_type_id, value, optional_value
    ):
        async with async_session() as session:
            if optional_value:
                category_property_value_id = await session.execute(
                    select(cls.id).where(
                        and_(
                            cls.property_type_id.__eq__(category_property_type_id),
                            cls.value.__eq__(value),
                            cls.optional_value.__eq__(optional_value),
                        )
                    )
                )
            else:
                category_property_value_id = await session.execute(
                    select(cls.id).where(
                        and_(
                            cls.property_type_id.__eq__(category_property_type_id),
                            cls.value.__eq__(value),
                        )
                    )
                )
            return category_property_value_id.scalar()


class CategoryVariationValueMixin:
    @classmethod
    async def get_category_variation_value_id(cls, category_variation_type_id, value):
        async with async_session() as session:
            category_variation_value_id = await session.execute(
                select(cls.id).where(
                    and_(
                        cls.variation_type_id.__eq__(category_variation_type_id),
                        cls.value.__eq__(value),
                    )
                )
            )
            return category_variation_value_id.scalar()


class TagsMixin:
    @classmethod
    async def get_tags_by_product_id(cls, product_id):
        async with async_session() as session:
            tags = await session.execute(
                select(cls.name).where(cls.product_id.__eq__(product_id))
            )
            return [row[0] for row in tags if tags]


@dataclass
class User(Base, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = Column(Integer, primary_key=True, nullable=False)
    first_name: Mapped[str] = Column(String(30), nullable=True)
    last_name: Mapped[str] = Column(String(30), nullable=True)
    email: Mapped[str] = Column(String(50), unique=True, index=True, nullable=False)
    phone: Mapped[str] = Column(String(20), nullable=True)
    datetime = Column(DateTime, nullable=False)
    is_supplier: Mapped[bool] = Column(Boolean, nullable=False)

    creds = relationship("UserCreds", back_populates="user")


@dataclass
class UserCreds(Base):
    __tablename__ = "user_creds"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    password: Mapped[str] = Column(Text, nullable=False)

    user = relationship("User", back_populates="creds")


@dataclass
class UserImage(Base):
    __tablename__ = "user_images"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    thumbnail_url: Mapped[str] = Column(Text, nullable=True)
    source_url: Mapped[str] = Column(Text, nullable=True)


@dataclass
class UserAdress(Base):
    __tablename__ = "user_addresses"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    country: Mapped[str] = Column(String(30), nullable=True)
    area: Mapped[str] = Column(String(50), nullable=True)
    city: Mapped[str] = Column(String(50), nullable=True)
    street: Mapped[str] = Column(String(100), nullable=True)
    building: Mapped[str] = Column(String(20), nullable=True)
    appartment: Mapped[str] = Column(String(20), nullable=True)
    postal_code: Mapped[str] = Column(String(20), nullable=True)


@dataclass
class UserNotification(Base):
    __tablename__ = "user_notifications"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    on_discount: Mapped[bool] = Column(Boolean, default=True)
    on_order_updates: Mapped[bool] = Column(Boolean, default=True)
    on_order_reminders: Mapped[bool] = Column(Boolean, default=True)
    on_stock_again: Mapped[bool] = Column(Boolean, default=True)
    on_product_is_cheaper: Mapped[bool] = Column(Boolean, default=True)
    on_your_favorites_new: Mapped[bool] = Column(Boolean, default=True)
    on_account_support: Mapped[bool] = Column(Boolean, default=True)


@dataclass
class Seller(Base, SellerMixin):
    __tablename__ = "sellers"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)


@dataclass
class Supplier(Base, SupplierMixin):
    __tablename__ = "suppliers"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    license_number: Mapped[int] = Column(Integer, nullable=True)
    grade_average: Mapped[float] = Column(DECIMAL(2, 1), default=0)
    additional_info: Mapped[str] = Column(Text, nullable=True)


@dataclass
class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = Column(Integer, primary_key=True)
    supplier_id: Mapped[int] = Column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )
    name: Mapped[str] = Column(String(100), nullable=True)
    is_manufacturer: Mapped[bool] = Column(Boolean, nullable=True)
    year_established: Mapped[int] = Column(Integer, nullable=True)
    number_of_employees: Mapped[int] = Column(Integer, nullable=True)
    description: Mapped[str] = Column(Text, nullable=True)
    phone: Mapped[str] = Column(String(20), nullable=True)
    business_email: Mapped[str] = Column(String(100), nullable=True)
    address: Mapped[str] = Column(Text, nullable=True)
    logo_url: Mapped[str] = Column(Text, nullable=True)
    business_sector: Mapped[str] = Column(String(100), nullable=False)
    photo_url: Mapped[str] = Column(Text, nullable=True)


@dataclass
class CompanyImages(Base):
    __tablename__ = "company_images"
    id: Mapped[int] = Column(Integer, primary_key=True)
    company_id: Mapped[int] = Column(
        Integer, ForeignKey("companies.id"), nullable=False
    )
    url: Mapped[str] = Column(Text, nullable=True)
    serial_number: Mapped[int] = Column(Integer, nullable=False)


@dataclass
class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)


@dataclass
class ResetToken(Base):
    __tablename__ = "reset_tokens"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    email: Mapped[str] = Column(String(50), nullable=False)
    reset_code: Mapped[str] = Column(String(50), nullable=False)
    status: Mapped[bool] = Column(Boolean, nullable=False)


@dataclass
class Product(Base, ProductMixin):
    __tablename__ = "products"
    id: Mapped[int] = Column(Integer, primary_key=True)
    supplier_id: Mapped[int] = Column(
        Integer, ForeignKey("suppliers.id"), nullable=False
    )
    category_id: Mapped[int] = Column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    name: Mapped[str] = Column(String(200), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    datetime = Column(DateTime, nullable=False)
    grade_average: Mapped[float] = Column(DECIMAL(2, 1), default=0)
    total_orders: Mapped[int] = Column(Integer, default=0)
    UUID: Mapped[str] = Column(String(36), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)


@dataclass
class Tags(Base, TagsMixin):
    __tablename__ = "tags"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
    name: Mapped[str] = Column(String(30), nullable=False)


@dataclass
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = Column(Integer, primary_key=True)
    seller_id: Mapped[int] = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    is_cart: Mapped[bool] = Column(Boolean, default=True)


@dataclass
class OrderStatus(Base):
    __tablename__ = "order_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)


@dataclass
class OrderProductVariation(Base):
    __tablename__ = "order_product_variations"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_variation_count_id: Mapped[int] = Column(
        Integer, ForeignKey("product_variation_counts.id"), nullable=False
    )
    order_id: Mapped[int] = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status_id: Mapped[int] = Column(
        Integer, ForeignKey("order_statuses.id"), nullable=False
    )
    count: Mapped[int] = Column(Integer, nullable=False)


@dataclass
class OrderNote(Base):
    __tablename__ = "order_notes"
    id: Mapped[int] = Column(Integer, primary_key=True)
    order_product_variation_id: Mapped[int] = Column(
        Integer, ForeignKey("order_product_variations.id"), nullable=False
    )
    text: Mapped[str] = Column(Text, nullable=False)


@dataclass
class ProductVariationCount(Base):
    __tablename__ = "product_variation_counts"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_variation_value1_id: Mapped[int] = Column(
        Integer, ForeignKey("product_variation_values.id"), nullable=False
    )
    product_variation_value2_id: Mapped[int] = Column(
        Integer, ForeignKey("product_variation_values.id"), nullable=True
    )
    count: Mapped[int] = Column(Integer, nullable=False)


@dataclass
class Category(Base, CategoryMixin):
    __tablename__ = "categories"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(50), nullable=False)
    parent_id: Mapped[int] = Column(Integer, nullable=True)


@dataclass
class ProductReview(Base):
    __tablename__ = "product_reviews"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id: Mapped[int] = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    text: Mapped[str] = Column(Text, nullable=False)
    grade_overall: Mapped[int] = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)


@dataclass
class ProductReviewReaction(Base):
    __tablename__ = "product_review_reactions"
    id: Mapped[int] = Column(Integer, primary_key=True)
    seller_id: Mapped[int] = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_review_id: Mapped[int] = Column(
        Integer, ForeignKey("product_reviews.id"), nullable=False
    )
    reaction: Mapped[bool] = Column(Boolean, nullable=False)


@dataclass
class ProductReviewPhoto(Base):
    __tablename__ = "product_review_photos"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_review_id: Mapped[int] = Column(
        Integer, ForeignKey("product_reviews.id"), nullable=False
    )
    image_url: Mapped[str] = Column(Text, nullable=False)
    serial_number: Mapped[int] = Column(Integer, nullable=False)


@dataclass
class ProductImage(Base, ProductImageMixin):
    __tablename__ = "product_images"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url: Mapped[str] = Column(Text, nullable=False)
    serial_number: Mapped[int] = Column(Integer, nullable=False)


@dataclass
class ProductPrice(Base):
    __tablename__ = "product_prices"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
    value: Mapped[float] = Column(DECIMAL(10, 2), nullable=False)
    discount: Mapped[float] = Column(DECIMAL(3, 2), nullable=True)
    min_quantity: Mapped[int] = Column(Integer, nullable=False)
    start_date = Column(
        DateTime, default=get_moscow_datetime()
    )
    end_date = Column(DateTime, nullable=True)


@dataclass
class UserSearch(Base):
    __tablename__ = "user_searches"
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    search_query: Mapped[Optional[str]] = Column(Text, nullable=False)
    datetime = Column(DateTime, nullable=False)


@dataclass
class CategoryProperty(Base):
    __tablename__ = "category_properties"
    id: Mapped[int] = Column(Integer, primary_key=True)
    category_id: Mapped[int] = Column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    property_type_id: Mapped[int] = Column(
        Integer, ForeignKey("category_property_types.id"), nullable=False
    )


@dataclass
class CategoryPropertyType(Base, CategoryPVTypeMixin):
    __tablename__ = "category_property_types"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(30), nullable=False)


@dataclass
class CategoryPropertyValue(Base, CategoryPropertyValueMixin):
    __tablename__ = "category_property_values"
    id: Mapped[int] = Column(Integer, primary_key=True)
    property_type_id: Mapped[int] = Column(
        Integer, ForeignKey("category_property_types.id"), nullable=False
    )
    value: Mapped[str] = Column(String(50), nullable=False)
    optional_value: Mapped[str] = Column(String(50), nullable=True)


@dataclass
class CategoryVariationType(Base, CategoryPVTypeMixin):
    __tablename__ = "category_variation_types"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(30), nullable=False)


@dataclass
class CategoryVariationValue(Base, CategoryVariationValueMixin):
    __tablename__ = "category_variation_values"
    id: Mapped[int] = Column(Integer, primary_key=True)
    variation_type_id: Mapped[int] = Column(
        Integer, ForeignKey("category_variation_types.id"), nullable=False
    )
    value: Mapped[str] = Column(String(50), nullable=False)


@dataclass
class CategoryVariation(Base):
    __tablename__ = "category_variations"
    id: Mapped[int] = Column(Integer, primary_key=True)
    category_id: Mapped[int] = Column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    variation_type_id: Mapped[int] = Column(
        Integer, ForeignKey("category_variation_types.id"), nullable=False
    )


@dataclass
class ProductPropertyValue(Base):
    __tablename__ = "product_property_values"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
    property_value_id: Mapped[int] = Column(
        Integer, ForeignKey("category_property_values.id"), nullable=False
    )


@dataclass
class ProductVariationValue(Base, ProductVariationValueMixin):
    __tablename__ = "product_variation_values"
    id: Mapped[int] = Column(Integer, primary_key=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
    variation_value_id: Mapped[int] = Column(
        Integer, ForeignKey("category_variation_values.id"), nullable=False
    )


@dataclass
class SellerFavorite(Base):
    __tablename__ = "seller_favorites"
    id: Mapped[int] = Column(Integer, primary_key=True)
    seller_id: Mapped[int] = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False)
