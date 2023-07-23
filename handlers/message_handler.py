import datetime
import logging
import traceback

import peewee
from aiogram import types
from aiogram.dispatcher import FSMContext, filters

import keyboard as km
import services
from instances import dp, bot, unlock_api
from states import UserState
from utils import models, messages
from utils.my_filters import IsAdmin
from utils.settings import SUPER_ADMIN


@dp.message_handler(commands="start")
async def start(message: types.Message):
    args = message.get_args()
    username = message.chat.username
    try:
        user = models.User.get(chat_id=message.chat.id)
        await bot.send_message(chat_id=message.chat.id, text=messages.already_met,
                               reply_markup=km.getMainKeyboard(user))
        return
    except:
        logging.info(f"User ({args}, {username if username is not None else ''}, {message.chat.id}) tries to log in")

    user_data = await unlock_api.register_user(username)
    logging.info(f"New user with data: {user_data}")

    user = models.User.create(chat_id=message.chat.id, id=user_data.id, first_name=user_data.first_name,
                              last_name=user_data.last_name)
    user.save()
    await bot.send_message(message.chat.id, messages.welcome_message.format(name=user.first_name),
                           reply_markup=km.getMainKeyboard(user))

    await bot.send_message(message.chat.id, messages.qr_code_view, reply_markup=km.getQRViewKeyboard())
    await bot.send_message(message.chat.id, messages.tutorial)


@dp.message_handler(IsAdmin(), commands="clear")
async def clear_keyboard(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=messages.cleared_message,
                           reply_markup=types.reply_keyboard.ReplyKeyboardRemove())


@dp.message_handler(IsAdmin(), commands="raise")
async def raise_error(message: types.Message):
    args = message.get_args()
    raise Exception(args)


@dp.message_handler(commands="admin")
async def clear_keyboard(message: types.Message):
    chat_id = message.chat.id
    if chat_id != SUPER_ADMIN:
        return

    try:
        args = message.text.split()[1]
        user = models.User.get((models.User.chat_id == int(args)))
        user.is_admin = True
        user.save()
    except:
        logging.error(traceback.format_exc())


@dp.message_handler(IsAdmin(), commands="webapp")
async def webapp_keyboard(message: types.Message):
    await bot.send_message(message.chat.id, "Hello", reply_markup=km.getQRScannerKeyboard())


@dp.message_handler(state=UserState.answering_question)
async def answer_question(message: types.Message, state: FSMContext):
    answer = message.text
    question_id = (await state.get_data())["question_id"]
    await state.finish()
    user = models.User.get((models.User.chat_id == message.chat.id))
    data = await unlock_api.sendAnswer(user.id, question_id, answer)
    await bot.send_message(message.chat.id, data["msg"])


# @dp.message_handler(state=UserState.entering_promocode)
# async def promocode_enter(message: types.Message, state: FSMContext):
#     promocode = message.text
#     chat_id = message.chat.id
#     await state.finish()
#     promocode_models = Promocode.select().where((Promocode.date == datetime.datetime.now().date().strftime("%Y-%m-%d")),
#                                                 (peewee.fn.LOWER(Promocode.code) == promocode.lower()))
#     if not len(promocode_models):
#         await bot.send_message(chat_id, messages.promocode_not_found_message)
#         return
#     user = models.User.get((models.User.chat_id == chat_id))
#     promocode_model: Promocode = promocode_models[0]
#     text = promocode_model.answer
#     photo = promocode_model.photo
#
#     data = await unlock_api.sendPromocode(user.id, promocode_model.id)
#     if data["success"]:
#         if text is not None:
#             await bot.send_message(chat_id, text)
#         if photo is not None:
#             await bot.send_photo(chat_id, photo)
#
#
#     else:
#         await bot.send_message(chat_id, data["msg"])


@dp.message_handler(IsAdmin(), state=UserState.admin_broadcast)
async def broadcast_message(message: types.Message, state: FSMContext):
    text_to_broadcast = message.text
    await state.finish()
    await services.broadcast(text_to_broadcast)


@dp.message_handler(filters.Text(equals=messages.score_request))
async def score_request(message: types.Message):
    chat_id = message.chat.id
    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return

    score = await unlock_api.getScore(user.id)
    await bot.send_message(chat_id, messages.score_message.format(score=score))


@dp.message_handler(filters.Text(equals=messages.daily_report))
async def daily_report(message: types.Message):
    chat_id = message.chat.id

    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return
    # do magic with api
    data = await unlock_api.getDaily(user.id)
    msg = data["msg"]
    daily_score = data["daily_score"]
    await bot.send_message(chat_id, messages.daily_report_message.format(report=msg,
                                                                         daily_score=daily_score))

@dp.message_handler(filters.Text(equals=messages.qr_request))
async def qr_request(message: types.Message):
    chat_id = message.chat.id

    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return

    await bot.send_message(chat_id, messages.qr_code_view, reply_markup=km.getQRViewKeyboard())

@dp.message_handler(IsAdmin(), filters.Text(equals=messages.turn_on_admin))
async def turn_on_admin_button(message: types.Message):
    chat_id = message.chat.id
    try:
        user: models.User = models.User.get(models.User.chat_id == chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return

    user.admin_mode = True
    user.save()
    await bot.send_message(user.chat_id, messages.admin_mode.format(state="Включен"),
                           reply_markup=km.getMainKeyboard(user))


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.turn_off_admin))
async def turn_off_admin_button(message: types.Message):
    chat_id = message.chat.id
    try:
        user: models.User = models.User.get(models.User.chat_id == chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return
    user.admin_mode = False
    user.save()
    await bot.send_message(user.chat_id, messages.admin_mode.format(state="Выключен"),
                           reply_markup=km.getMainKeyboard(user))


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.broadcast))
async def promocode_button(message: types.Message):
    await UserState.admin_broadcast.set()
    await bot.send_message(message.chat.id, messages.enter_text_to_broadcast_message)


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.back))
async def back_button(message: types.Message):
    chat_id = message.chat.id
    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return
    await bot.send_message(message.chat.id, messages.ok_message,
                           reply_markup=km.getMainKeyboard(user))
