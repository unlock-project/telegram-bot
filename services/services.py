import asyncio
import hashlib
import json
import logging
import traceback
import typing
import hmac

import keyboard as km
import schemas
import utils.settings

from utils import models, messages
from instances import bot
from utils.settings import CHANNEL_ID
from urllib.parse import unquote


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


async def edit_registration(msg_id: int, registration_id: int, registration_text: str, options) -> int:
    keyboard = km.getRegistrationKeyboard(registration_id, options)

    try:
        result = await bot.edit_message_text(registration_text, CHANNEL_ID, msg_id, reply_markup=keyboard)
        return result.message_id
    except:
        logging.error(traceback.format_exc())
        logging.error(CHANNEL_ID)


async def get_option_by_id(options: list, option_id: int) -> dict | None:
    for option in options:
        if option['option_id'] == option_id:
            return option
    return None


async def validate_user(init_data, c_str="WebAppData"):
    """
    Validates the data received from the Telegram web app, using the
    method documented here:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    hash_str - the has string passed by the webapp
    init_data - the query string passed by the webapp
    c_str - constant string (default = "WebAppData")
    """
    init_data = sorted([chunk.split("=")
                        for chunk in unquote(init_data).split("&")],
                       key=lambda x: x[0])
    hash_str = ""
    chat_id = 0
    for rec in init_data:
        if rec[0] == "hash":
            hash_str = rec[1]
        elif rec[0] == "user":
            chat_id = json.loads(rec[1])['id']
    if not hash_str:
        return False
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data if rec[0] != "hash"])
    secret_key = hmac.new(c_str.encode(), utils.settings.BOT_TOKEN.encode(),
                          hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data.encode(),
                          hashlib.sha256)

    return {'valid': data_check.hexdigest() == hash_str, 'chat_id': chat_id}
