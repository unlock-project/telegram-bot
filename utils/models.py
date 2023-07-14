from peewee import *
from playhouse.postgres_ext import JSONField
from utils.settings import DB_USER, DB_HOST, DB_NAME, DB_PASS, DB_PORT

db = PostgresqlDatabase(DB_NAME, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    chat_id = BigIntegerField(null=False, primary_key=True)
    id = IntegerField(null=False)
    is_admin = BooleanField(default=False)
    admin_mode = BooleanField(default=False)


class Vote(BaseModel):
    vote_id = IntegerField(primary_key=True)
    vote_text = TextField()
    options = JSONField()
    message_id = IntegerField()

#
#
# class Choice(BaseModel):
#     name = TextField()
#     vote = ForeignKeyField(Vote)
#
#
# class Question(BaseModel):
#     id = IntegerField(primary_key=True)
#     title = TextField(null=True)
#     text = TextField()
#     date = DateField()
#     time = TimeField()


#
#
# class Promocode(BaseModel):
#     id = IntegerField(primary_key=True)
#     title = TextField(null=True)
#     code = TextField()
#     answer = TextField(null=True)
#     photo = TextField(null=True)
#     date = DateField()
#     time = TimeField()
#
#
class Registration(BaseModel):
    registration_id = IntegerField(primary_key=True)
    registration_text = TextField(null=True)
    options = JSONField()
    message_id = IntegerField()

#
# class Option(BaseModel):
#     title = TextField()
#     registration = ForeignKeyField(Registration)
#     count = IntegerField()
#     max = IntegerField(null=True)


db.connect()
