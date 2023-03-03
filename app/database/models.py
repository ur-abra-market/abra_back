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
from sqlalchemy.orm import relationship, column_property, declared_attr
from sqlalchemy.sql import func

from .init import async_session
from app.logic.consts import *
from app.logic.queries import *
from app.logic.utils import get_moscow_datetime
from app.logic.exceptions import InvalidStatusId, InvalidProductVariationId

from fastapi.encoders import jsonable_encoder

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

    @classmethod
    async def get_user_number(cls, email):
        async with async_session() as session:
            phone_number = await session.execute(
                select(cls.phone).where(cls.email.__eq__(email))
            )
            return phone_number.scalar()


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


class OrderStatusMixin:
    @classmethod
    async def get_all_statuses(cls):
        async with async_session() as session:
            query = select(cls)
            result = await session.execute(query)
            return {int(row.id): row.name for row in result.scalars().all()}

    @classmethod
    async def get_status(cls, id):
        async with async_session() as session:
            result = await session.get(cls, id)
            if result is None:
                raise InvalidStatusId("Invalid status_id")
            return result


class OrderProductVariationMixin:
    @classmethod
    async def get_order_product_variation(cls, id):
        async with async_session() as session:
            result = await session.get(OrderProductVariation, id)
            if result is None:
                raise InvalidProductVariationId("Invalid order_product_variation_id")
            return result

    @classmethod
    async def change_status(cls, product_id, status_id):
        async with async_session() as session:
            order_product = await cls.get_order_product_variation(product_id)
            order_product.status_id = status_id
            session.add(order_product)
            await session.commit()
            return order_product


class CompanyMixin:
    @classmethod
    async def get_company_id_by_supplier_id(cls, supplier_id):
        async with async_session() as session:
            company_id = await session.execute(
                select(cls.id).where(cls.supplier_id.__eq__(supplier_id))
            )
            return company_id.scalar()


class PropertyDisplayTypeMixin:
    @classmethod
    async def get_display_name_by_property(cls, property_name: str):
        async with async_session() as session:
            display_type = (
                await session.execute(
                    select(cls.display_property_name)
                    .join(CategoryPropertyType)
                    .where(CategoryPropertyType.name.__eq__(property_name))
                )
            ).all()
            display_type = jsonable_encoder(display_type)
            return display_type


@dataclass
class User(Base, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    fullname = column_property(first_name + " " + last_name)

    email = Column(String(50), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    datetime = Column(DateTime(timezone=True), server_default=func.now())
    is_supplier = Column(Boolean, nullable=False)
    creds = relationship("UserCreds", uselist=False)
    supplier = relationship("Supplier", uselist=False, back_populates="user")
    seller = relationship("Seller", uselist=False, back_populates="user")
    images = relationship("UserImage", uselist=True)
    addresses = relationship("UserAdress", uselist=True)
    notifications = relationship("UserNotification", uselist=False)


@dataclass
class UserCreds(Base):
    __tablename__ = "user_creds"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    password = Column(Text, nullable=False)


@dataclass
class UserImage(Base):
    __tablename__ = "user_images"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)


@dataclass
class UserAdress(Base):
    __tablename__ = "user_addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    country = Column(String(30), nullable=True)
    area = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    street = Column(String(100), nullable=True)
    building = Column(String(20), nullable=True)
    appartment = Column(String(20), nullable=True)
    postal_code = Column(String(20), nullable=True)


@dataclass
class UserNotification(Base):
    __tablename__ = "user_notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    on_discount = Column(Boolean, default=True)
    on_order_updates = Column(Boolean, default=True)
    on_order_reminders = Column(Boolean, default=True)
    on_stock_again = Column(Boolean, default=True)
    on_product_is_cheaper = Column(Boolean, default=True)
    on_your_favorites_new = Column(Boolean, default=True)
    on_account_support = Column(Boolean, default=True)


@dataclass
class Seller(Base, SellerMixin):
    __tablename__ = "sellers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="seller")

    favorites = relationship(
        "Product",
        secondary="seller_favorites",
        back_populates="favorites_by_users",
        uselist=True,
    )


@dataclass
class Supplier(Base, SupplierMixin):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    license_number = Column(String(25), nullable=True)
    grade_average = Column(DECIMAL(2, 1), default=0)
    additional_info = Column(Text, nullable=True)
    user = relationship("User", back_populates="supplier")
    company = relationship("Company", uselist=False, back_populates="supplier")
    products = relationship("Product", uselist=True, back_populates="supplier")


@dataclass
class Company(Base, CompanyMixin):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    name = Column(String(100), nullable=True)
    is_manufacturer = Column(Boolean, nullable=True)
    year_established = Column(Integer, nullable=True)
    number_of_employees = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    business_email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    business_sector = Column(String(100), nullable=True)
    photo_url = Column(Text, nullable=True)
    supplier = relationship("Supplier", back_populates="company")


@dataclass
class CompanyImages(Base):
    __tablename__ = "company_images"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    url = Column(Text, nullable=True)
    serial_number = Column(Integer, nullable=False)


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
class Product(Base, ProductMixin):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    datetime = Column(DateTime, nullable=False)
    grade_average = Column(DECIMAL(2, 1), default=0)
    total_orders = Column(Integer, default=0)
    UUID = Column(String(36), nullable=False)
    is_active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="products", uselist=False)
    supplier = relationship("Supplier", back_populates="products", uselist=False)
    tags = relationship("Tags", back_populates="product", uselist=True)
    properties = relationship(
        "CategoryPropertyValue",
        secondary="product_property_values",
        back_populates="products",
        uselist=True,
    )
    variations = relationship(
        "CategoryVariationValue",
        secondary="product_variation_values",
        back_populates="products",
        uselist=True,
    )
    favorites_by_users = relationship(
        "Seller", secondary="seller_favorites", back_populates="favorites", uselist=True
    )


@dataclass
class Tags(Base, TagsMixin):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(30), nullable=False)

    product = relationship("Product", back_populates="tags")


@dataclass
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    datetime = Column(DateTime, nullable=False)
    is_cart = Column(Boolean, default=True)


@dataclass
class OrderStatus(Base, OrderStatusMixin):
    __tablename__ = "order_statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)


@dataclass
class OrderProductVariation(Base, OrderProductVariationMixin):
    __tablename__ = "order_product_variations"
    id = Column(Integer, primary_key=True)
    product_variation_count_id = Column(
        Integer, ForeignKey("product_variation_counts.id"), nullable=False
    )
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("order_statuses.id"), nullable=False)
    count = Column(Integer, nullable=False)


@dataclass
class OrderNote(Base):
    __tablename__ = "order_notes"
    id = Column(Integer, primary_key=True)
    order_product_variation_id = Column(
        Integer, ForeignKey("order_product_variations.id"), nullable=False
    )
    text = Column(Text, nullable=False)


@dataclass
class ProductVariationCount(Base):
    __tablename__ = "product_variation_counts"
    id = Column(Integer, primary_key=True)
    product_variation_value1_id = Column(
        Integer, ForeignKey("product_variation_values.id"), nullable=False
    )
    product_variation_value2_id = Column(
        Integer, ForeignKey("product_variation_values.id"), nullable=True
    )
    count = Column(Integer, nullable=False)


@dataclass
class Category(Base, CategoryMixin):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, nullable=True)
    level = Column(Integer, nullable=False)

    products = relationship("Product", back_populates="category", uselist=True)
    properties = relationship(
        "CategoryPropertyType",
        secondary="category_properties",
        back_populates="category",
        uselist=True,
    )
    variations = relationship(
        "CategoryVariationType",
        secondary="category_variations",
        back_populates="category",
        uselist=True,
    )


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
    product_review_id = Column(
        Integer, ForeignKey("product_reviews.id"), nullable=False
    )
    reaction = Column(Boolean, nullable=False)


@dataclass
class ProductReviewPhoto(Base):
    __tablename__ = "product_review_photos"
    id = Column(Integer, primary_key=True)
    product_review_id = Column(
        Integer, ForeignKey("product_reviews.id"), nullable=False
    )
    image_url = Column(Text, nullable=False)
    serial_number = Column(Integer, nullable=False)


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
    value = Column(DECIMAL(10, 2), nullable=False)
    discount = Column(DECIMAL(3, 2), nullable=True)
    min_quantity = Column(Integer, nullable=False)
    start_date = Column(DateTime, default=get_moscow_datetime())
    end_date = Column(DateTime, nullable=True)

    @declared_attr
    def value_price(cls) -> float:
        return column_property(cls.value)


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
    property_type_id = Column(
        Integer, ForeignKey("category_property_types.id"), nullable=False
    )


@dataclass
class CategoryPropertyType(Base, CategoryPVTypeMixin):
    __tablename__ = "category_property_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

    category = relationship(
        "Category",
        secondary="category_properties",
        back_populates="properties",
        uselist=True,
    )
    values = relationship("CategoryPropertyValue", back_populates="type", uselist=True)


@dataclass
class CategoryPropertyValue(Base, CategoryPropertyValueMixin):
    __tablename__ = "category_property_values"
    id = Column(Integer, primary_key=True)
    property_type_id = Column(
        Integer, ForeignKey("category_property_types.id"), nullable=False
    )
    value = Column(String(50), nullable=False)
    optional_value = Column(String(50), nullable=True)

    type = relationship("CategoryPropertyType", back_populates="values")
    products = relationship(
        "Product",
        secondary="product_property_values",
        back_populates="properties",
        uselist=True,
    )


@dataclass
class CategoryVariationType(Base, CategoryPVTypeMixin):
    __tablename__ = "category_variation_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

    category = relationship(
        "Category",
        secondary="category_variations",
        back_populates="variations",
        uselist=True,
    )
    values = relationship("CategoryVariationValue", back_populates="type", uselist=True)


@dataclass
class CategoryVariationValue(Base, CategoryVariationValueMixin):
    __tablename__ = "category_variation_values"
    id = Column(Integer, primary_key=True)
    variation_type_id = Column(
        Integer, ForeignKey("category_variation_types.id"), nullable=False
    )
    value = Column(String(50), nullable=False)

    type = relationship("CategoryVariationType", back_populates="values")
    products = relationship(
        "Product",
        secondary="product_variation_values",
        back_populates="variations",
        uselist=True,
    )


@dataclass
class CategoryVariation(Base):
    __tablename__ = "category_variations"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    variation_type_id = Column(
        Integer, ForeignKey("category_variation_types.id"), nullable=False
    )


@dataclass
class ProductPropertyValue(Base):
    __tablename__ = "product_property_values"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    property_value_id = Column(
        Integer, ForeignKey("category_property_values.id"), nullable=False
    )


@dataclass
class ProductVariationValue(Base, ProductVariationValueMixin):
    __tablename__ = "product_variation_values"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variation_value_id = Column(
        Integer, ForeignKey("category_variation_values.id"), nullable=False
    )


@dataclass
class SellerFavorite(Base):
    __tablename__ = "seller_favorites"
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)


@dataclass
class UserPaymentCred(Base):
    __tablename__ = "user_payment_creds"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_holder = Column(String(30), nullable=False)
    card_number = Column(String(30), nullable=False)
    expired_date = Column(String(10), nullable=False)
