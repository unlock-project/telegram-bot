import asyncio
import hashlib
import hmac
import json
import logging
import traceback
import typing
from urllib.parse import unquote

import aiogram.utils.exceptions
import requests

import catcher
import keyboard as km
import schemas
import utils.settings
from instances import bot
from lib.function_wrapper import supervised
from lib.latest_throttled_executor import RetryAfterException
from utils import models, messages
from utils.models import Registration
from utils.settings import CHANNEL_ID, UNLOCK_API_TOKEN, UNLOCK_API_URL


class InTaskException(Exception):
    original: Exception
    payload: dict

    def __init__(self, original: Exception, payload: dict):
        self.original = original
        self.payload = payload


async def broadcast(message_text: str):
    users = models.User.select()
    for user in users:

        successful = False
        while not successful:
            await asyncio.sleep(0.040)  # not more than 30 per second (25)
            successful = True
            try:
                await bot.send_message(user.chat_id, message_text,
                                       reply_markup=km.getMainKeyboard(user))
            except aiogram.utils.exceptions.RetryAfter as exception:
                logging.warning(f"Flood control exceeded. Waiting {exception.timeout}")
                await asyncio.sleep(exception.timeout)
                successful = False
            except Exception as ex:
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
        successful = False
        while not successful:
            await asyncio.sleep(0.040)  # not more than 30 per second (25)
            successful = True
            try:
                await bot.send_message(user.chat_id, question_text,
                                       reply_markup=km.getAnswerKeyboard(question_id))
            except aiogram.utils.exceptions.RetryAfter as exception:
                logging.warning(f"Flood control exceeded. Waiting {exception.timeout}")
                await asyncio.sleep(exception.timeout)
                successful = False
            except Exception as ex:
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

async def update_option(options: list[dict], option_id: int, new_option_text: str) -> list[dict]:
    for option in options:
        if option['option_id'] == option_id:
            option['option_text'] = new_option_text
    return options

@supervised
async def update_registration(msg_id: int, registration_id: int, option_id: int, option_text: str) -> int:
    registration = Registration.get_or_none(Registration.registration_id==registration_id)
    options = await update_option(registration.options, option_id, option_text)
    registration.options = options
    registration.save()

    mapped_options = []
    for option in options:
        mapped_options.append(schemas.Option(**option))


    keyboard = km.getRegistrationKeyboard(registration.registration_id, mapped_options)

    try:
        await bot.edit_message_reply_markup(CHANNEL_ID, msg_id, reply_markup=keyboard)
    except aiogram.utils.exceptions.MessageNotModified as ex:
        logging.warning(str(ex))
        raise RetryAfterException(500)
    except aiogram.utils.exceptions.RetryAfter as ex:
        raise RetryAfterException(ex.timeout * 1000)



async def send_scanners(event_id: int, users: typing.List[int], event_name: str):
    chat_ids = models.User.select(models.User.chat_id).where(models.User.id.in_(users))

    for chat_id in chat_ids:

        successful = False
        while not successful:
            await asyncio.sleep(0.040)  # not more than 30 per second (25)
            successful = True
            try:
                await bot.send_message(chat_id, messages.scanner_message.format(event_name=event_name),
                                       reply_markup=km.getQRScannerKeyboard(event_id))
            except aiogram.utils.exceptions.RetryAfter as exception:
                logging.warning(f"Flood control exceeded. Waiting {exception.timeout}")
                await asyncio.sleep(exception.timeout)
                successful = False
            except Exception as ex:
                logging.error(traceback.format_exc())
                logging.error(chat_id)



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


async def log_error(error, update):
    report = catcher.collect(error)
    html = catcher.formatters.HTMLFormatter().format(report, maxdepth=1)
    result = requests.post(f"{UNLOCK_API_URL}/bot/api/error", params={'token': UNLOCK_API_TOKEN},
                           data={'data': str(update)}, files={'traceback': html})
    if result.ok:
        result_data = result.json()
        await bot.send_message(utils.settings.SUPER_ADMIN, messages.error_report
                               .format(error_id=result_data["error_id"],
                                       error_url=f'{UNLOCK_API_URL}{result_data["error_url"]}'))


def task_done_callback(task: asyncio.Task):
    exception = task.exception()
    if exception is not None:

        if isinstance(exception, InTaskException):
            payload = exception.payload
            f_ex = exception.original
        else:
            f_ex = exception
            payload = {"from": "task"}
        logging.error(str(exception))
        asyncio.get_running_loop().create_task(log_error(f_ex, payload))
