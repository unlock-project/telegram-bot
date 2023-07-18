from sqlalchemy import Column, BigInteger, Integer, Boolean, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    chat_id = Column(BigInteger, nullable=False, primary_key=True)
    id = Column(Integer, nullable=False)
    is_admin = Column(Boolean, default=False)
    admin_mode = Column(Boolean, default=False)


class Vote(Base):
    __tablename__ = "votes"

    vote_id = Column(Integer, primary_key=True)
    vote_text = Column(String)
    options = Column(JSON)
    message_id = Column(Integer)


class Registration(Base):
    __tablename__ = "registrations"

    registration_id = Column(Integer, primary_key=True)
    registration_text = Column(String, nullable=True)
    options = Column(JSON)
    message_id = Column(Integer)