import asyncio
import logging
import traceback

import aiogram

import keyboard as km

from utils import models, messages


#  Сохранять статус для возобновления в случае падения.
async def broadcast(bot: aiogram.Bot, text: str):
    users = models.User.select()
    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, text, reply_markup=km.getMainKeyboard(user))
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_voting(bot: aiogram.Bot, vote_id: int, vote: str, choices):
    users = models.User.select()
    keyboard = km.getVoteKeyboard(vote_id, choices)

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, vote, reply_markup=keyboard)
        except:

            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_question(bot: aiogram.Bot, question_id: int):
    users = models.User.select()

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, messages.question_arrived_message,
                                   reply_markup=km.getAnswerKeyboard(question_id))
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_registration(bot: aiogram.Bot, registration_id: int, registration_text: str, options):
    users = models.User.select()
    keyboard = km.getRegistrationKeyboard(registration_id, options)

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, registration_text, reply_markup=keyboard)
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)