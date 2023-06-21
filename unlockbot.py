import asyncio
import datetime
import json
import logging
import traceback

import peewee
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiohttp import web

from server import AppBundle
from utils import config
from utils import messages
from utils import models
from utils.keyboards import KeyboardManager
from utils.models import Promocode, Vote, Choice, Registration, Option, Question
from utils.my_filters import IsAdmin, CallbackType
from utils.qr import generate_and_save
from utils.unlockapi import UnlockAPI

km = KeyboardManager()

bot = Bot(token=config.getToken(), parse_mode="HTML")

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

dp.filters_factory.bind(IsAdmin)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/log-{datetime.datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)

unlock_api = UnlockAPI(config.getUnlockApiURL())
app = AppBundle()


class UserState(StatesGroup):
    entering_promocode = State()
    admin_broadcast = State()
    answering_question = State()


async def broadcast(text: str):
    users = models.User.select()
    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, text, reply_markup=km.getMainKeyboard(user))
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_voting(vote_id: int, vote: str, choices):
    users = models.User.select()
    keyboard = km.getVoteKeyboard(vote_id, choices)

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, vote, reply_markup=keyboard)
        except:

            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_question(question_id: int):
    users = models.User.select()

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, messages.question_arrived_message,
                                   reply_markup=km.getAnswerKeyboard(question_id))
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


async def start_registration(registration_id: int, registration_text: str, options):
    users = models.User.select()
    keyboard = km.getRegistrationKeyboard(registration_id, options)

    for user in users:
        await asyncio.sleep(0.040)  # not more than 30 per second (25)
        try:
            await bot.send_message(user.chat_id, registration_text, reply_markup=keyboard)
        except:
            logging.error(traceback.format_exc())
            logging.error(user.id)


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
    # await unlock_api.sendPromocode(user.id, promocode_model.id)


# if data["success"]:
#     await bot.edit_message_text(callback.message.text + f"\n\n {messages.voted.format(choice=choice.name)}",
#                                 chat_id,
#                                 callback.message.message_id)
# else:
#     await bot.send_message(chat_id, data["msg"])
#     await callback.answer()


@dp.message_handler(IsAdmin(), state=UserState.admin_broadcast)
async def broadcast_message(message: types.Message, state: FSMContext):
    text_to_broadcast = message.text
    await state.finish()
    await broadcast(text_to_broadcast)


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


@dp.callback_query_handler(CallbackType("vote"))
async def make_choice_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)
    choice = Choice.get_by_id(data['choice'])
    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return
    data = await unlock_api.sendVoteChoice(user.id, choice.vote.id, choice.name)

    if data["success"]:
        await bot.edit_message_text(callback.message.text + f"\n\n {messages.voted.format(choice=choice.name)}",
                                    chat_id,
                                    callback.message.message_id)
    else:
        await bot.send_message(chat_id, data["msg"])
        await callback.answer()
    return


@dp.callback_query_handler(CallbackType("vote_select"))
async def vote_select_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id

    data = json.loads(callback.data)
    await callback.message.delete()
    vote_id = data["id"]
    if vote_id == -1:
        return
    votes_list = Vote.select().where(Vote.id == vote_id)

    if not len(votes_list):
        await bot.send_message(chat_id, messages.data_not_found_message)
        return

    vote_model: Vote = votes_list[0]
    choices_select = Choice.select().where(Choice.vote == vote_model)
    if not len(choices_select):
        await bot.send_message(chat_id, messages.data_not_found_message)
        return

    await start_voting(vote_model.id, vote_model.title, choices_select)


@dp.callback_query_handler(CallbackType("question_select"))
async def question_select_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id

    data = json.loads(callback.data)
    await callback.message.delete()
    question_id = data["id"]
    if question_id == -1:
        return
    questions_list = Question.select().where(Question.id == question_id)

    if not len(questions_list):
        await bot.send_message(chat_id, messages.data_not_found_message)
        return

    question_model: Question = questions_list[0]

    await start_question(question_model.id)


@dp.callback_query_handler(CallbackType("registration_select"))
async def registration_select_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id

    data = json.loads(callback.data)
    await callback.message.delete()
    registration_id = data["id"]
    if registration_id == -1:
        return
    registrations_list = Registration.select().where(Registration.id == registration_id)

    if not len(registrations_list):
        await bot.send_message(chat_id, messages.data_not_found_message)
        return

    registration_model: Registration = registrations_list[0]

    options_select = Option.select().where(Option.registration == registration_model)
    if not len(options_select):
        await bot.send_message(chat_id, messages.data_not_found_message)
        return

    await start_registration(registration_model.id, registration_model.text, options_select)


@dp.callback_query_handler(CallbackType("answer"))
async def answer_button_event(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)
    await callback.message.delete()
    questions_list = Question.select().where(Question.id == data["id"])

    if not len(questions_list):
        await bot.send_message(chat_id, messages.data_not_found_message)
        return

    question_model: Question = questions_list[0]

    await bot.send_message(chat_id, messages.question_message.format(question=question_model.text))

    await UserState.answering_question.set()
    await state.update_data({"question_id": question_model.id})
    return


@dp.callback_query_handler(CallbackType("registration"))
async def make_choice_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)
    option = Option.get_by_id(data['option'])
    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met)
        return
    # await bot.edit_message_text(callback.message.text + f"\n\n {messages.voted.format(option=option.title)}", chat_id,
    #                             callback.message.message_id)

    data = await unlock_api.sendRegistration(user.id, option.registration.id, option.title)
    await bot.send_message(chat_id, data["msg"])
    if not data["success"]:
        await callback.answer()
    else:
        await callback.message.delete()

    return


@app.post('/sendMessage')
async def apiMessage(request: web.Request):
    if request.content_type != 'application/json':
        return web.json_response({'reason': 'non-json data'}, status=400)
    body = await request.json()
    if 'chat_id' not in body or 'message' not in body:
        return web.json_response({'reason': 'has no expected data'}, status=400)
    try:
        chat_id = int(body['chat_id'])
        message = body['message']
        await bot.send_message(chat_id, message)
    except Exception as ex:
        return web.json_response({'reason': ex.args}, status=400)
    return web.json_response({'ok': True}, status=200)


if __name__ == "__main__":
    app.run(bot, dp)
