import asyncio
import logging
import traceback
import typing

import keyboard as km
import schemas

from utils import models, messages
from instances import bot
from utils.settings import CHANNEL_ID


#  Сохранять статус для возобновления в случае падения.
async def broadcast(message_text: str):
    users = models.User.select()
    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, message_text, reply_markup=km.getMainKeyboard(user))
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_voting(vote_id: int, vote_text: str, options: typing.List[schemas.Option]) -> int:
    keyboard = km.getVoteKeyboard(vote_id, options)
    try:
        result = await bot.send_message(CHANNEL_ID, vote_text, reply_markup=keyboard)
        return result.message_id
    except:
        logging.error(traceback.format_exc())
        logging.error(CHANNEL_ID)


async def start_question(question_text: str, question_id: int):
    users = models.User.select()

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, question_text,
                                   reply_markup=km.getAnswerKeyboard(question_id))
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_registration(registration_id: int, registration_text: str, options) -> int:
    keyboard = km.getRegistrationKeyboard(registration_id, options)

    try:
        result = await bot.send_message(CHANNEL_ID, registration_text, reply_markup=keyboard)
        return result.message_id
    except:
        logging.error(traceback.format_exc())
        logging.error(CHANNEL_ID)


async def get_option_by_id(options: list, option_id: int) -> dict | None:
    for option in options:
        if option['option_id'] == option_id:
            return option
    return None
