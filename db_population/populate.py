import asyncio
import logging
import colorlog
import random
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from const import first_names, last_names, MIN_USERS_COUNT
from app.database.init import async_session
from app.database.models import (
    User,
    Supplier,
    Seller,
    UserAdress,
    Company,
    UserNotification,
    Product,
)


async def populate_suppliers_data(count) -> None:
    logging.info(":: Generating suppliers... ::")
    users = []
    for i in range(1, count + 1):
        first_name = first_names[random.randrange(0, len(first_names))]
        last_name = last_names[random.randrange(0, len(last_names))]

        phone_length = random.randrange(9, 12)
        phone = str(random.randint(10 ** (phone_length - 1), (10**phone_length) - 1))

        license_number_length = random.randrange(10, 15)
        license_number = str(
            random.randint(
                10 ** (license_number_length - 1), (10**license_number_length) - 1
            )
        )

        users.append(
            User(
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name}.{last_name}@gmail.com",
                phone=phone,
                is_supplier=True,
                supplier=Supplier(
                    license_number=license_number,
                    grade_average=0,
                    additional_info="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                ),
                addresses=[
                    UserAdress(
                        country="USA",
                        area="test area",
                        city="Washington DC",
                        street="Some street",
                        building="25",
                        appartment="155",
                        postal_code="14545135",
                    )
                ],
                company=Company(
                    name=f"{first_name} {last_name} Company",
                    is_manufacturer=True,
                    year_established=2022,
                    number_of_employees=random.randrange(10, 31),
                    description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
                    phone=phone,
                    business_email=f"{last_name}.{first_name}@gmail.com",
                    address="USA, Washington DC, Lucky street, building 5, appartment 55",
                    logo_url="https://rb.gy/6zvp2r",
                    business_sector="Clothes",
                ),
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
    logging.info(":: Generating sellers... ::")
    users = []
    for i in range(1, count + 1):
        first_name = first_names[random.randrange(0, len(first_names))]
        last_name = last_names[random.randrange(0, len(last_names))]

        phone_length = random.randrange(9, 12)
        phone = str(random.randint(10 ** (phone_length - 1), (10**phone_length) - 1))

        users.append(
            User(
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name}.{last_name}@gmail.com",
                phone=phone,
                is_supplier=True,
                seller=Seller(),
                addresses=[
                    UserAdress(
                        country="USA",
                        area="test area",
                        city="Washington DC",
                        street="Some street",
                        building="25",
                        appartment="155",
                        postal_code="14545135",
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
    logging.info(":: Getting categories... ::")
    logging.info(":: Populating categories... ::")


async def populate_products_data(count) -> None:
    logging.info(":: Generating products... ::")
    products: list = []

    try:
        async with async_session() as session:
            suppliers = await (session.execute(select(Supplier))).all()
    except SQLAlchemyError as e:
        logging.error(e)

    for supplier in suppliers:
        for i in range(1, count + 1):
            products.append(Product(
                category_id=,
                name=,
                description=,
                datetime=,
                grade_average=,
                total_orders=,
                UUID=,
                is_active=True,
            ))
        supplier.products.extend(products)

    logging.info(":: Populating products... ::")
    try:
        async with async_session() as session:
            await session.commit()
    except SQLAlchemyError as e:
        logging.error(e)


async def check_users() -> bool:
    logging.info(":: Checking for data... ::")
    try:
        async with async_session() as session:
            users = (await session.execute(select(User))).all()
            return len(users) >= MIN_USERS_COUNT
    except SQLAlchemyError as e:
        logging.error(e)
        return False


async def run_process() -> None:
    logging.info(":: Starting population into db ::")
    if await check_users():
        logging.info(":: No need to perform population ::")
        return
    await populate_suppliers_data(count=2)
    await populate_sellers_data(count=2)
    await populate_categories_data()
    await populate_products_data(count=100)
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
