from os import getenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


db_credentials = "mysql+aiomysql://{user}:{password}@{host}:{port}/{db_name}".format(
    user=getenv("RDS_USERNAME"),
    password=getenv("RDS_PASSWORD"),
    host=getenv("RDS_HOSTNAME"),
    port=getenv("RDS_PORT"),
    db_name=getenv("RDS_DB_NAME"),
)

engine = create_async_engine(db_credentials, pool_recycle=60 * 5)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
