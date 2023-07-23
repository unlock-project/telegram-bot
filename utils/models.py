import inspect
import logging
import traceback

import aiohttp.web
from peewee import *
from playhouse.postgres_ext import JSONField
from utils.settings import DB_USER, DB_HOST, DB_NAME, DB_PASS, DB_PORT

db = PostgresqlDatabase(DB_NAME, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, autorollback=True)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    chat_id = BigIntegerField(null=False, primary_key=True)
    id = IntegerField(null=False)
    is_admin = BooleanField(default=False)
    admin_mode = BooleanField(default=False)
    first_name = TextField()
    last_name = TextField()


class Vote(BaseModel):
    vote_id = IntegerField(primary_key=True)
    vote_text = TextField()
    options = JSONField()
    message_id = IntegerField()


class Registration(BaseModel):
    registration_id = IntegerField(primary_key=True)
    registration_text = TextField(null=True)
    options = JSONField()
    message_id = IntegerField()


async def connect(app: aiohttp.web.Application):
    try:
        db.connect()
    except Exception as ex:
        logging.critical(traceback.format_exc())
        raise ex
    try:
        db.create_tables([User, Vote, Registration])
    except OperationalError as er:
        logging.warning(str(er))

async def cleanup(app: aiohttp.web.Application):
    db.close()
    logging.info("DB connection closed")
