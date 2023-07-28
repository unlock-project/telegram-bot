import json

from aiogram import types

import services
from instances import dp, bot
from utils import messages
from utils.models import Vote, Registration, User
from utils.my_filters import CallbackType
from utils.settings import BOT_USERNAME


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
        await bot.answer_callback_query(callback.id, messages.not_met.format(bot=BOT_USERNAME), show_alert=True)
        return
    # data = await unlock_api.sendVoteChoice(user.id, choice.vote.id, choice.name)
    #
    # if data["success"]:
    #     await bot.edit_message_text(callback.message.text + f"\n\n {messages.voted.format(choice=choice.name)}",
    #                                 chat_id,
    #                                 callback.message.message_id)
    # else:
    #     await bot.send_message(chat_id, data["msg"])
    #     await callback.answer()
    # return
    await bot.answer_callback_query(callback.id, f'Вы проголосвали за {option["option_text"]}', show_alert=True)


# @dp.callback_query_handler(CallbackType("answer"))
# async def answer_button_event(callback: types.CallbackQuery, state: FSMContext):
#     chat_id = callback.from_user.id
#     data = json.loads(callback.data)
#     await callback.message.delete()
#     questions_list = Question.select().where(Question.id == data["id"])
#
#     if not len(questions_list):
#         await bot.send_message(chat_id, messages.data_not_found_message)
#         return
#
#     question_model: Question = questions_list[0]
#
#     await bot.send_message(chat_id, messages.question_message.format(question=question_model.text))
#
#     await UserState.answering_question.set()
#     await state.update_data({"question_id": question_model.id})
#     return


@dp.callback_query_handler(CallbackType("registration"))
async def make_choice_event(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    data = json.loads(callback.data)
    registration = Registration.get_or_none(Registration.registration_id == data['id'])
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
        await bot.answer_callback_query(callback.id, messages.not_met.format(bot=BOT_USERNAME), show_alert=True)
        return
    # await bot.edit_message_text(callback.message.text + f"\n\n {messages.voted.format(option=option.title)}", chat_id,
    #                             callback.message.message_id)

    # data = await unlock_api.sendRegistration(user.id, option.registration.id, option.title)
    # await bot.send_message(chat_id, data["msg"])
    # if not data["success"]:
    #     await callback.answer()
    # else:
    #     await callback.message.delete()
    await bot.answer_callback_query(callback.id, f'Вы зарегистрировались на {option["option_text"]}', show_alert=True)
