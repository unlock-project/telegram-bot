import datetime
import logging
import traceback

import peewee
from aiogram import types
from aiogram.dispatcher import FSMContext, filters

import services
from instances import dp, bot, unlock_api
from states import UserState
from utils import models, messages
import keyboard as km
from utils.models import Vote, Registration
from utils.my_filters import IsAdmin
from utils.qr import generate_and_save


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

    data = await unlock_api.sendUserData(username, args)
    logging.info(f"New user with data: {data}")
    if "data" not in data.keys():
        await bot.send_message(message.chat.id, messages.user_not_found)
        return

    user_object = data["data"]

    user = models.User.create(chat_id=message.chat.id, id=user_object["id"])
    user.save()
    await bot.send_message(message.chat.id, messages.welcome_message.format(name=user_object["first"]),
                           reply_markup=km.getMainKeyboard(user))
    if "qr" in user_object.keys() and user_object["qr"] is not None:
        qr_data = user_object["qr"]
        qr_file = await generate_and_save(user, qr_data)
        await bot.send_message(message.chat.id, messages.qr_code_message)
        await bot.send_photo(message.chat.id, photo=open(qr_file, "rb").read())
    await bot.send_message(message.chat.id, messages.tutorial)


@dp.message_handler(IsAdmin(), commands="clear")
async def clear_keyboard(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=messages.cleared_message,
                           reply_markup=types.reply_keyboard.ReplyKeyboardRemove())


@dp.message_handler(IsAdmin(), commands="qr")
async def qr_generate(message: types.Message):
    args = message.get_args()
    if not args:
        return
    user: models.User = models.User.get((models.User.chat_id == message.chat.id))
    path = await generate_and_save(user, args)
    await bot.send_photo(message.chat.id, photo=open(path, "rb").read())


@dp.message_handler(IsAdmin(), commands="admin")
async def clear_keyboard(message: types.Message):
    chat_id = message.chat.id
    if chat_id != 1074893653 and chat_id != 313961073:
        return

    try:
        args = message.text.split()[1]
        user = models.User.get((models.User.chat_id == int(args)))
        user.is_admin = True
        user.save()
    except:
        logging.error(traceback.format_exc())


@dp.message_handler(state=UserState.answering_question)
async def answer_question(message: types.Message, state: FSMContext):
    answer = message.text
    question_id = (await state.get_data())["question_id"]
    await state.finish()
    user = models.User.get((models.User.chat_id == message.chat.id))
    data = await unlock_api.sendAnswer(user.id, question_id, answer)
    await bot.send_message(message.chat.id, data["msg"])


@dp.message_handler(state=UserState.entering_promocode)
async def promocode_enter(message: types.Message, state: FSMContext):
    promocode = message.text
    chat_id = message.chat.id
    await state.finish()
    promocode_models = Promocode.select().where((Promocode.date == datetime.datetime.now().date().strftime("%Y-%m-%d")),
                                                (peewee.fn.LOWER(Promocode.code) == promocode.lower()))
    if not len(promocode_models):
        await bot.send_message(chat_id, messages.promocode_not_found_message)
        return
    user = models.User.get((models.User.chat_id == chat_id))
    promocode_model: Promocode = promocode_models[0]
    text = promocode_model.answer
    photo = promocode_model.photo

    data = await unlock_api.sendPromocode(user.id, promocode_model.id)
    if data["success"]:
        if text is not None:
            await bot.send_message(chat_id, text)
        if photo is not None:
            await bot.send_photo(chat_id, photo)


    else:
        await bot.send_message(chat_id, data["msg"])


@dp.message_handler(IsAdmin(), state=UserState.admin_broadcast)
async def broadcast_message(message: types.Message, state: FSMContext):
    text_to_broadcast = message.text
    await state.finish()
    await services.broadcast(bot, text_to_broadcast)


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


@dp.message_handler(filters.Text(equals=messages.promocode))
async def promocode_button(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, messages.enter_promocode_message)
    await UserState.entering_promocode.set()


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


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.update_db))
async def update_db(message: types.Message):
    result = await unlock_api.update_db()
    if result:
        await bot.send_message(message.chat.id, messages.updated_message)
    else:
        await bot.send_message(message.chat.id, messages.error_message)


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.votes))
async def votes_list(message: types.Message):
    votes_list = Vote.select().where(Vote.date == datetime.datetime.now().strftime("%Y-%m-%d")).order_by(Vote.time)
    if not len(votes_list):
        await bot.send_message(message.chat.id, messages.data_not_found_message)
        return

    await bot.send_message(message.chat.id, messages.choose_what_to_send_message,
                           reply_markup=km.getVotesListKeyboard(votes_list))


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.registrations))
async def registrations_list(message: types.Message):
    registrations_list = (Registration.select()
                          .where(Registration.date == datetime.datetime.now().strftime("%Y-%m-%d"))
                          .order_by(Registration.time))
    if not len(registrations_list):
        await bot.send_message(message.chat.id, messages.data_not_found_message)
        return

    await bot.send_message(message.chat.id, messages.choose_what_to_send_message,
                           reply_markup=km.getRegistrationsKeyboard(registrations_list))


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.questions))
async def questions_list(message: types.Message):
    questions_list = (Question.select()
                      .where(Question.date == datetime.datetime.now().strftime("%Y-%m-%d"))
                      .order_by(Question.time))
    if not len(questions_list):
        await bot.send_message(message.chat.id, messages.data_not_found_message)
        return

    await bot.send_message(message.chat.id, messages.choose_what_to_send_message,
                           reply_markup=km.getQuestionsListKeyboard(questions_list))