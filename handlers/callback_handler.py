import asyncio
import json

from aiogram import types
from aiogram.dispatcher import FSMContext

import services
from instances import dp, bot, unlock_api
from states import UserState
from utils import messages
from utils.models import Vote, Registration, User
from utils.my_filters import CallbackType
from utils import settings


@dp.callback_query_handler(CallbackType("vote"))
async def make_choice_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)
    vote = Vote.get_or_none(Vote.vote_id == data['id'])
    if vote is None:
        await bot.answer_callback_query(callback.id, 'Произошла ошибка, попробуйте позже')
        raise Exception("Bad callback data")
    option = await services.get_option_by_id(vote.options, data['option'])
    if option is None:
        await bot.answer_callback_query(callback.id, 'Произошла ошибка, попробуйте позже')
        raise Exception("Bad callback data")
    try:
        user = User.get(chat_id=chat_id)
    except:
        await bot.answer_callback_query(callback.id, messages.not_met.format(bot=settings.BOT_USERNAME), show_alert=True)
        return
    data = await unlock_api.vote_choose(vote.vote_id, user.id, option["option_id"])
    await bot.answer_callback_query(callback.id, data.text, show_alert=True)


@dp.callback_query_handler(CallbackType("answer"))
async def answer_button_event(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)

    if 'id' not in data:
        await bot.send_message(chat_id, messages.error_message)
        await callback.message.delete()
        raise KeyError(f'No \'id\' in question keyboard data keys')

    await bot.send_message(chat_id, messages.question_message)
    await callback.answer('')
    await UserState.answering_question.set()
    await state.update_data({"question_id": data['id'], 'message_id': callback.message.message_id})


@dp.callback_query_handler(CallbackType("registration"))
async def make_choice_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)
    registration: Registration = Registration.get_or_none(Registration.registration_id == data['id'])
    if registration is None:
        await bot.answer_callback_query(callback.id, 'Произошла ошибка, попробуйте позже')
        # ERROR
    option = await services.get_option_by_id(registration.options, data['option'])
    if option is None:
        await bot.answer_callback_query(callback.id, 'Произошла ошибка, попробуйте позже')
        # ERROR
    try:
        user = User.get(chat_id=chat_id)
    except:
        await bot.answer_callback_query(callback.id, messages.not_met.format(bot=settings.BOT_USERNAME), show_alert=True)
        return

    data = await unlock_api.registration_choose(registration.registration_id, user.id, option["option_id"])


    await bot.answer_callback_query(callback.id, data.message, show_alert=True)
    asyncio.get_running_loop().create_task(services.update_registration(callback.message.message_id, registration.registration_id, data.option_id,
                                 data.new_text)) \
        .add_done_callback(services.services.task_done_callback)
