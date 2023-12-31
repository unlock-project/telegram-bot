# generated by datamodel-codegen:
#   filename:  back.api.yaml
#   timestamp: 2023-08-03T16:41:43+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, constr


class UserSchema(BaseModel):
    id: int = Field(..., title='ID')
    first_name: constr(max_length=150) = Field(..., title='First Name')
    last_name: constr(max_length=150) = Field(..., title='Last Name')
    qr: constr(max_length=100) = Field(..., title='Qr')
    team: Optional[int] = Field(None, title='Team')


class BotRegisterSchema(BaseModel):
    username: str = Field(..., title='Username')


class TeamSchema(BaseModel):
    name: constr(max_length=100) = Field(..., title='Name')
    balance: float = Field(..., title='Balance')
    tutor: int = Field(..., title='Tutor')


class EventSchema(BaseModel):
    message: str = Field(...)

class BalanceSchema(BaseModel):
    user_id: int = Field(...)
    balance: int = Field(...)


class PromoSchema(BaseModel):
    code: str = Field(..., title='Code')
    text: str = Field(..., title='Text')


class PromoBotSchema(BaseModel):
    code: str = Field(..., title='Code')
    user_id: int = Field(..., title='User Id')


class MessageSchema(BaseModel):
    text: str = Field(..., title='Text')


class AnswerBotSchema(BaseModel):
    question_id: int = Field(..., title='Question Id')
    user_id: int = Field(..., title='User Id')
    answer: Optional[str] = Field(None, title='Answer')


class RegistrationSchema(BaseModel):
    registration_id: int = Field(...)
    option_id: int = Field(...)
    new_text: str = Field(...)
    message: str = Field(...)


class OptionBotSchema(BaseModel):
    registration_id: int = Field(..., title='Registration Id')
    user_id: int = Field(..., title='User Id')
    option_id: int = Field(..., title='Option Id')


class ChoiceBotSchema(BaseModel):
    vote_id: int = Field(..., title='Vote Id')
    user_id: int = Field(..., title='User Id')
    option_id: int = Field(..., title='Option Id')

class ReportSchema(BaseModel):
    user_id: int = Field(...)
    report_text: str = Field(...)

class ReportResponse(BaseModel):
    report_id: int = Field(...)
    report_status: str = Field(...)