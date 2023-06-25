import json

from aiogram import types
from aiogram.dispatcher import FSMContext

import services
from instances import dp, bot, unlock_api
from states import UserState
from utils import models, messages
from utils.models import Vote, Registration, Question, Option, Choice
from utils.my_filters import CallbackType


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

    await services.start_voting(bot, vote_model.id, vote_model.title, choices_select)


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

    await services.start_question(bot, question_model.id)


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

    await services.start_registration(bot, registration_model.id, registration_model.text, options_select)


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