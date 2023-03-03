import asyncio
import uuid
import csv
import logging
import colorlog
import random
from datetime import datetime
from faker import Faker
from faker.providers.phone_number import Provider as PhoneNumberProvider
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from const import MIN_SUPPLIERS_COUNT, MIN_SELLERS_COUNT, MIN_PRODUCT_COUNT_BY_SUPPLIER
from app.database.init import async_session
from app.database.models import (
    User,
    Supplier,
    Seller,
    UserAdress,
    UserCreds,
    Company,
    UserNotification,
    Product,
    Category,
    ProductVariationValue,
    CategoryVariationValue,
    CategoryVariationType,
    CategoryVariation,
    CategoryProperty,
    CategoryPropertyType,
    CategoryPropertyValue,
    ProductPropertyValue,
)
from app.logic.pwd_hashing import hash_password


class OurPhoneNumberProvider(PhoneNumberProvider):
    def our_phone_number(self):
        return self.msisdn()[3:]


faker: Faker = Faker()
faker.add_provider(OurPhoneNumberProvider)


async def populate_suppliers_data(count) -> None:
    logging.info(":: Checking suppliers... ::")
    try:
        async with async_session() as session:
            suppliers = (await session.execute(select(Supplier.id))).all()
            if len(suppliers) >= MIN_SUPPLIERS_COUNT:
                logging.info(":: No need to perform population, skipping... ::")
                return
    except SQLAlchemyError as e:
        logging.error(e)

    logging.info(":: Generating suppliers... ::")
    users = []
    for i in range(1, count + 1):
        license_number_length = random.randrange(10, 15)
        license_number = str(
            random.randint(
                10 ** (license_number_length - 1), (10**license_number_length) - 1
            )
        )

        users.append(
            User(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                phone=faker.our_phone_number(),
                is_supplier=True,
                creds=UserCreds(password=hash_password("Qwerty!12345")),
                supplier=Supplier(
                    license_number=license_number,
                    grade_average=0,
                    additional_info=faker.paragraph(
                        nb_sentences=random.randrange(5, 11)
                    ),
                    company=Company(
                        name=faker.company() + " " + faker.company_suffix(),
                        is_manufacturer=bool(random.getrandbits(1)),
                        year_established=random.randrange(1990, 2023),
                        number_of_employees=random.randrange(10, 31),
                        description=faker.paragraph(
                            nb_sentences=random.randrange(5, 11)
                        ),
                        phone=faker.our_phone_number(),
                        business_email=faker.email(),
                        address=faker.address(),
                        logo_url="https://rb.gy/6zvp2r",
                        business_sector="Clothes",
                    ),
                ),
                addresses=[
                    UserAdress(
                        country=faker.country(),
                        area="some area",
                        city=faker.city(),
                        street=faker.street_name(),
                        building=faker.building_number(),
                        appartment=faker.secondary_address(),
                        postal_code=faker.postcode(),
                    )
                ],
                notifications=UserNotification(
                    on_discount=bool(random.getrandbits(1)),
                    on_order_updates=bool(random.getrandbits(1)),
                    on_order_reminders=bool(random.getrandbits(1)),
                    on_stock_again=bool(random.getrandbits(1)),
                    on_product_is_cheaper=bool(random.getrandbits(1)),
                    on_your_favorites_new=bool(random.getrandbits(1)),
                    on_account_support=bool(random.getrandbits(1)),
                ),
            )
        )

    logging.info(":: Populating suppliers... ::")
    try:
        async with async_session() as session:
            session.add_all(users)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)


async def populate_sellers_data(count) -> None:
    logging.info(":: Checking sellers... ::")
    try:
        async with async_session() as session:
            sellers = (await session.execute(select(Seller.id))).all()
            if len(sellers) >= MIN_SELLERS_COUNT:
                logging.info(":: No need to perform population, skipping... ::")
                return
    except SQLAlchemyError as e:
        logging.error(e)

    logging.info(":: Generating sellers... ::")
    users = []
    for i in range(1, count + 1):
        users.append(
            User(
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                email=faker.email(),
                phone=faker.our_phone_number(),
                is_supplier=False,
                creds=UserCreds(password=hash_password("Qwerty!12345")),
                seller=Seller(),
                addresses=[
                    UserAdress(
                        country=faker.country(),
                        area="some area",
                        city=faker.city(),
                        street=faker.street_name(),
                        building=faker.building_number(),
                        appartment=faker.secondary_address(),
                        postal_code=faker.postcode(),
                    )
                ],
                notifications=UserNotification(
                    on_discount=bool(random.getrandbits(1)),
                    on_order_updates=bool(random.getrandbits(1)),
                    on_order_reminders=bool(random.getrandbits(1)),
                    on_stock_again=bool(random.getrandbits(1)),
                    on_product_is_cheaper=bool(random.getrandbits(1)),
                    on_your_favorites_new=bool(random.getrandbits(1)),
                    on_account_support=bool(random.getrandbits(1)),
                ),
            )
        )

    logging.info(":: Populating sellers... ::")
    try:
        async with async_session() as session:
            session.add_all(users)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)


async def populate_categories_data() -> None:
    logging.info(":: Checking categories... ::")
    try:
        async with async_session() as session:
            cats = (await session.execute(select(Category.id))).all()
            if cats:
                logging.info(":: No need to perform population, skipping... ::")
                return
    except SQLAlchemyError as e:
        logging.error(e)

    logging.info(":: Generating properties and variations... ::")
    properties = [
        CategoryPropertyType(
            id=1,
            name="Material",
            values=[
                CategoryPropertyValue(id=1, value="Cotton", optional_value="50%"),
                CategoryPropertyValue(id=2, value="Cotton", optional_value="70%"),
                CategoryPropertyValue(id=3, value="Elastane", optional_value="60%"),
                CategoryPropertyValue(id=4, value="Elastane", optional_value="80%"),
            ],
        ),
        CategoryPropertyType(
            id=2,
            name="Age Group",
            values=[
                CategoryPropertyValue(
                    id=5,
                    value="Adults",
                ),
                CategoryPropertyValue(
                    id=6,
                    value="Children",
                ),
            ],
        ),
        CategoryPropertyType(
            id=3,
            name="Gender",
            values=[
                CategoryPropertyValue(
                    id=7,
                    value="Women",
                ),
                CategoryPropertyValue(
                    id=8,
                    value="Men",
                ),
            ],
        ),
        CategoryPropertyType(
            id=4,
            name="Technics",
            values=[
                CategoryPropertyValue(
                    id=9,
                    value="Printed",
                ),
                CategoryPropertyValue(
                    id=10,
                    value="Non-printed",
                ),
            ],
        ),
        CategoryPropertyType(
            id=5,
            name="Age Group",
            values=[
                CategoryPropertyValue(
                    id=11,
                    value="Adults",
                ),
                CategoryPropertyValue(
                    id=12,
                    value="Children",
                ),
            ],
        ),
    ]
    variations = [
        CategoryVariationType(
            id=1,
            name="Color",
            values=[
                CategoryVariationValue(
                    id=1,
                    value="Red",
                ),
                CategoryVariationValue(
                    id=2,
                    value="Orange",
                ),
                CategoryVariationValue(
                    id=3,
                    value="Yellow",
                ),
                CategoryVariationValue(
                    id=4,
                    value="Green",
                ),
                CategoryVariationValue(
                    id=5,
                    value="Blue",
                ),
                CategoryVariationValue(
                    id=6,
                    value="Purple",
                ),
                CategoryVariationValue(
                    id=7,
                    value="Black",
                ),
                CategoryVariationValue(
                    id=8,
                    value="White",
                ),
            ],
        ),
        CategoryVariationType(
            id=2,
            name="Size",
            values=[
                CategoryVariationValue(
                    id=9,
                    value="10",
                ),
                CategoryVariationValue(
                    id=10,
                    value="20",
                ),
                CategoryVariationValue(
                    id=11,
                    value="30",
                ),
                CategoryVariationValue(
                    id=12,
                    value="40",
                ),
                CategoryVariationValue(
                    id=13,
                    value="50",
                ),
                CategoryVariationValue(
                    id=14,
                    value="60",
                ),
                CategoryVariationValue(
                    id=15,
                    value="70",
                ),
                CategoryVariationValue(
                    id=16,
                    value="80",
                ),
            ],
        ),
    ]

    logging.info(":: Populating properties and variations... ::")
    try:
        async with async_session() as session:
            session.add_all([*properties, *variations])
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)

    logging.info(":: Getting categories... ::")
    cats = []
    with open("db_population/cats.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            cat = Category(
                id=row[0],
                name=row[1],
                parent_id=row[2] if row[2] else None,
                level=row[3],
            )
            cats.append(cat)

    logging.info(":: Populating categories... ::")
    try:
        async with async_session() as session:
            session.add_all(cats)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)

    logging.info(":: Updating categories ::")
    try:
        async with async_session() as session:
            properties = (await session.execute(select(CategoryPropertyType.id))).all()
            variations = (await session.execute(select(CategoryVariationType.id))).all()
            cats = (await session.execute(select(Category.id))).all()
    except SQLAlchemyError as e:
        logging.error(e)

    cat_properties = []
    cat_variations = []
    for cat in cats:
        for property in properties:
            cat_properties.append(
                CategoryProperty(
                    category_id=cat.id,
                    property_type_id=property.id,
                )
            )
        for variation in variations:
            cat_variations.append(
                CategoryVariation(
                    category_id=cat.id,
                    variation_type_id=variation.id,
                )
            )

    try:
        async with async_session() as session:
            session.add_all([*cat_properties, *cat_variations])
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)


async def populate_products_data(count) -> None:
    logging.info(":: Checking products... ::")
    try:
        async with async_session() as session:
            suppliers = (await session.execute(select(Supplier.id))).all()
            products = (await session.execute(select(Product.id))).all()
            cats = (
                await session.execute(
                    select(Category.id).where(Category.level.__eq__(3))
                )
            ).all()
            cats = [cat.id for cat in cats]
    except SQLAlchemyError as e:
        logging.error(e)

    if len(products) >= (MIN_PRODUCT_COUNT_BY_SUPPLIER * len(suppliers)):
        logging.info(":: No need to perform population, skipping... ::")
        return

    logging.info(":: Generating products... ::")
    products: list = []

    for supplier in suppliers:
        for i in range(1, count + 1):
            products.append(
                Product(
                    supplier_id=supplier.id,
                    category_id=random.choice(cats),
                    name=" ".join(faker.words(random.randrange(3, 10))),
                    description=faker.paragraph(nb_sentences=random.randrange(5, 11)),
                    datetime=faker.date_between_dates(
                        date_start=datetime(2015, 1, 1),
                    ),
                    grade_average=0,
                    total_orders=random.randrange(0, 1000),
                    UUID=uuid.uuid1(),
                    is_active=True,
                )
            )

    logging.info(":: Populating products... ::")
    try:
        async with async_session() as session:
            session.add_all(products)
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)


async def run_process() -> None:
    logging.info(":: Starting population into db ::")
    await populate_suppliers_data(count=MIN_SUPPLIERS_COUNT)
    await populate_sellers_data(count=MIN_SELLERS_COUNT)
    await populate_categories_data()
    await populate_products_data(count=MIN_PRODUCT_COUNT_BY_SUPPLIER)
    logging.info(":: Population ended successfully ::")


if __name__ == "__main__":
    handler = logging.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt="%(log_color)s%(levelname)s%(reset)s \t\t | %(asctime)s.%(msecs)03d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # general logging setup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run_process())
