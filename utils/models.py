from peewee import *

db = SqliteDatabase('models.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    chat_id = IntegerField(null=False, primary_key=True)
    id = IntegerField(null=False)
    is_admin = BooleanField(default=False)
    admin_mode = BooleanField(default=False)


class Vote(BaseModel):
    id = IntegerField(primary_key=True)
    title = TextField()
    date = DateField()
    time = TimeField()


class Choice(BaseModel):
    name = TextField()
    vote = ForeignKeyField(Vote)


class Question(BaseModel):
    id = IntegerField(primary_key=True)
    title = TextField(null=True)
    text = TextField()
    date = DateField()
    time = TimeField()


class Promocode(BaseModel):
    id = IntegerField(primary_key=True)
    title = TextField(null=True)
    code = TextField()
    answer = TextField(null=True)
    photo = TextField(null=True)
    date = DateField()
    time = TimeField()


class Registration(BaseModel):
    id = IntegerField(primary_key=True)
    title = TextField(null=True)
    text = TextField()
    date = DateField()
    time = TimeField()


class Option(BaseModel):
    title = TextField()
    count = IntegerField()
    max = IntegerField(null=True)
    registration = ForeignKeyField(Registration)


db.connect()