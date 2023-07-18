import logging

import aiohttp.web
from aiohttp.web_runner import GracefulExit
from sqlalchemy import create_engine
from playhouse.postgres_ext import JSONField
from sqlalchemy import Column, String, Integer, Enum, ARRAY, Float, ForeignKey, BigInteger, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from utils.settings import DB_USER, DB_HOST, DB_NAME, DB_PASS, DB_PORT

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_aiopg(app: aiohttp.web.Application):
    app['pg_engine'] = await cre

