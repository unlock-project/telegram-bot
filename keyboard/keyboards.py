import json
import typing

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, \
    InlineKeyboardButton, WebAppInfo

import schemas
from utils import messages
from utils.models import User
from utils.settings import UNLOCK_API_URL


def getQRScannerKeyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Перейти", web_app=WebAppInfo(url=f'{UNLOCK_API_URL}bot/scanner')))
    return kb

def getQRViewKeyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Посмотреть", web_app=WebAppInfo(url=f'{UNLOCK_API_URL}bot/qr')))
    return kb


def getVotesListKeyboard(votes):
    votes_list = InlineKeyboardMarkup()

    for vote in votes:
        data = {"type": "vote_select", "id": vote.id}
        votes_list.add(InlineKeyboardButton(text=vote.title, callback_data=json.dumps(data)))

    data = {"type": "vote_select", "id": -1}
    votes_list.add(InlineKeyboardButton(text=messages.cancel, callback_data=json.dumps(data)))

    return votes_list


def getQuestionsListKeyboard(questions):
    questions_list = InlineKeyboardMarkup()

    for question in questions:
        data = {"type": "question_select", "id": question.id}
        questions_list.add(InlineKeyboardButton(text=question.title, callback_data=json.dumps(data)))

    data = {"type": "question_select", "id": -1}
    questions_list.add(InlineKeyboardButton(text=messages.cancel, callback_data=json.dumps(data)))

    return questions_list


def getRegistrationKeyboard(registration_id: int, options: typing.List[schemas.Option]):
    registration_keyboard = InlineKeyboardMarkup()

    for option in options:
        data = json.dumps({"type": "registration", "id": registration_id, "option": option.option_id})
        registration_keyboard.add(InlineKeyboardButton(text=option.option_text, callback_data=data))

    return registration_keyboard


def getRegistrationsKeyboard(registrations):
    registrations_list = InlineKeyboardMarkup()

    for registration in registrations:
        data = {"type": "registration_select", "id": registration.id}
        registrations_list.add(InlineKeyboardButton(text=registration.title, callback_data=json.dumps(data)))

    data = {"type": "registration_select", "id": -1}
    registrations_list.add(InlineKeyboardButton(text=messages.cancel, callback_data=json.dumps(data)))

    return registrations_list


def getAnswerKeyboard(question_id: int):
    answerkeyboard = InlineKeyboardMarkup()
    data = dict(type="answer", id=question_id)
    answerkeyboard.add(InlineKeyboardButton(text=messages.answer, callback_data=json.dumps(data)))
    return answerkeyboard


def getCancelKeyboard():
    keyboard = types.reply_keyboard.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(messages.cancel)
    return keyboard


def getVoteKeyboard(vote_id: int, options: typing.List[schemas.Option]):
    vote_keyboard = InlineKeyboardMarkup()

    for option in options:
        data = json.dumps({"type": "vote", "id": vote_id, "option": option.option_id})
        vote_keyboard.add(InlineKeyboardButton(text=option.option_text, callback_data=data))

    return vote_keyboard


def getMainKeyboard(user: User):
    keyboard = types.reply_keyboard.ReplyKeyboardMarkup(resize_keyboard=True)
    if user.admin_mode:
        # admin keyboard
        keyboard.add(messages.broadcast)
        keyboard.add(messages.update_db)
        keyboard.add(messages.votes)
        keyboard.add(messages.questions)
        keyboard.add(messages.registrations)
        keyboard.add(messages.turn_off_admin)
    else:
        keyboard.add(messages.score_request, messages.daily_report, messages.promocode)
        keyboard.add(messages.qr_request)
        if user.is_admin:
            keyboard.add(messages.turn_on_admin)
    return keyboard
