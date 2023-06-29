from peewee import *
from playhouse.postgres_ext import JSONField

db = PostgresqlDatabase('unlockbot', host='localhost', port=5432, user='postgres', password='postgres')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    chat_id = IntegerField(null=False, primary_key=True)
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
db.create_tables([User, Vote, Registration])
