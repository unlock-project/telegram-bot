import logging
import traceback

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineQuery

import keyboard as km
import services
from instances import dp, bot, unlock_api
from states import UserState, InTunnelData
from unlockapi.errors import ResponseException
from utils import models, messages
from utils.models import User
from utils.my_filters import IsAdmin
from utils import settings
from utils.settings import SUPER_ADMIN




@dp.message_handler(filters.Text(equals=messages.stop_tunnel), state=UserState.in_tunnel)
async def stop_tunnel(message: types.Message, state: FSMContext):
    companion_data = InTunnelData(**(await state.get_data()))
    await state.storage.finish(chat=companion_data.companion_chat_id)
    await state.finish()
    user = User.get_or_none(User.chat_id == message.chat.id)
    companion = User.get_or_none(User.chat_id == companion_data.companion_chat_id)

    await bot.send_message(chat_id=message.chat.id, text="Диалог завершен",
                           reply_markup=km.getMainKeyboard(user) if user is not None else None)
    await bot.send_message(chat_id=companion_data.companion_chat_id,
                           text=f"{companion_data.role} завершил диалог",
                           reply_markup=km.getMainKeyboard(companion) if companion is not None else None)

@dp.message_handler(state=UserState.in_tunnel, content_types='any')
async def in_tunnel(message: types.Message, state: FSMContext):
    if message.content_type == "poll":
        return
    companion_data = InTunnelData(**(await state.get_data()))
    await bot.copy_message(chat_id=companion_data.companion_chat_id, from_chat_id=message.chat.id,
                           message_id=message.message_id)

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
    try:
        user_data = await unlock_api.register_user(username)
    except Exception as ex:
        logging.error(str(ex))
        await bot.send_message(message.chat.id, messages.user_not_found)
        return
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
async def make_admin(message: types.Message):
    chat_id = message.chat.id
    if chat_id != SUPER_ADMIN:
        return
    super_admin: User = User.get_or_none(chat_id=chat_id)
    if super_admin is None:
        return
    try:
        args = message.text.split()[1]
        user = models.User.get((models.User.chat_id == int(args)))
        if user.is_admin:
            await bot.send_message(chat_id, messages.already_admin)
            return
        user.is_admin = True
        user.save()
        await bot.send_message(user.chat_id, messages.became_admin.format(admin_name=f'{super_admin.first_name} {super_admin.last_name}'))
        await bot.send_message(chat_id, messages.appointed_admin.format(user_name=f'{user.first_name} {user.last_name}'))
    except:
        logging.error(traceback.format_exc())

@dp.message_handler(commands="revoke")
async def revoke_admin(message: types.Message):
    chat_id = message.chat.id
    if chat_id != SUPER_ADMIN:
        return
    super_admin: User = User.get_or_none(chat_id=chat_id)
    if super_admin is None:
        return
    try:
        args = message.text.split()[1]
        user = models.User.get((models.User.chat_id == int(args)))
        user.is_admin = False
        if not user.is_admin:
            await bot.send_message(chat_id, messages.not_admin)
            return
        user.save()
        await bot.send_message(user.chat_id, messages.no_longer_admin.format(admin_name=f'{super_admin.first_name} {super_admin.last_name}'))
        await bot.send_message(chat_id, messages.revoked_admin.format(user_name=f'{user.first_name} {user.last_name}'))
    except:
        logging.error(traceback.format_exc())

@dp.message_handler(IsAdmin(), commands="ban")
async def ban_user(message: types.Message):
    chat_id = message.chat.id
    admin: User = User.get_or_none(chat_id=chat_id)
    if admin is None:
        return
    try:
        args = message.text.split()[1]
        user = models.User.get((models.User.chat_id == int(args)))
        if user.is_banned:
            await bot.send_message(chat_id, messages.already_banned)
            return
        user.is_banned = True
        user.save()
        await bot.send_message(user.chat_id, messages.banned_user.format(admin_name=f'{admin.first_name} {admin.last_name}'))
        await bot.send_message(chat_id, messages.ban_user.format(user_name=f'{user.first_name} {user.last_name}'))
    except:
        logging.error(traceback.format_exc())

@dp.message_handler(IsAdmin(), commands="unban")
async def ban_user(message: types.Message):
    chat_id = message.chat.id
    admin: User = User.get_or_none(chat_id=chat_id)
    if admin is None:
        return
    try:
        args = message.text.split()[1]
        user = models.User.get((models.User.chat_id == int(args)))
        if not user.is_banned:
            await bot.send_message(chat_id, messages.not_banned)
            return
        user.is_banned = False
        user.save()
        await bot.send_message(user.chat_id, messages.unbanned_user.format(admin_name=f'{admin.first_name} {admin.last_name}'))
        await bot.send_message(chat_id, messages.unban_user.format(user_name=f'{user.first_name} {user.last_name}'))
    except:
        logging.error(traceback.format_exc())

@dp.message_handler(IsAdmin(), commands="webapp")
async def webapp_keyboard(message: types.Message):
    await bot.send_message(message.chat.id, "Hello", reply_markup=km.getTestQRScannerKeyboard())


@dp.message_handler(state=UserState.answering_question)
async def answer_question(message: types.Message, state: FSMContext):
    answer = message.text
    state_data = (await state.get_data())
    question_id = state_data["question_id"]
    message_id = state_data["message_id"]
    await state.finish()
    user = models.User.get((models.User.chat_id == message.chat.id))
    try:
        data = (await unlock_api.question_answer(question_id, user.id, answer))
    except Exception as ex:
        await bot.send_message(message.chat.id, messages.error_message)
        raise ex
    await bot.send_message(message.chat.id, data.text)
    await bot.edit_message_reply_markup(message.chat.id, message_id, reply_markup='')


@dp.message_handler(filters.Text(equals=messages.promocode))
async def promo_message(message: types.Message):
    await UserState.entering_promocode.set()
    await bot.send_message(message.chat.id, messages.enter_promocode_message)

@dp.message_handler(state=UserState.entering_promocode)
async def promocode_enter(message: types.Message, state: FSMContext):
    promocode = message.text
    chat_id = message.chat.id
    await state.finish()

    user = models.User.get_or_none(User.chat_id == chat_id)
    if user is None:
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return
    try:
        result = await unlock_api.promo_activate(promocode, user.id)
    except Exception as ex:
        await bot.send_message(message.chat.id, messages.error_message)
        raise ex
    await bot.send_message(chat_id, result.text)


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
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return

    try:
        data = await unlock_api.get_balance(user.id)
    except Exception as ex:
        await bot.send_message(message.chat.id, messages.error_message)
        raise ex
    await bot.send_message(chat_id, messages.score_message.format(score=data.balance))


@dp.message_handler(filters.Text(equals=messages.daily_report))
async def daily_report(message: types.Message):
    chat_id = message.chat.id

    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return
    # do magic with api
    try:
        data = await unlock_api.events_today(user.id)
    except ResponseException as ex:
        if ex.status_code == 404 and ex.has_reason:
            await bot.send_message(chat_id, messages.no_event_today)
            return
        else:
            await bot.send_message(message.chat.id, messages.error_message)
            raise ex
    except Exception as ex:
        await bot.send_message(message.chat.id, messages.error_message)
        raise ex

    if not data.message:
        await bot.send_message(chat_id, messages.no_event_today)
        return
    await bot.send_message(chat_id, messages.daily_report_message.format(report=data.message))

@dp.message_handler(filters.Text(equals=messages.team_report))
async def team_report(message: types.Message):
    chat_id = message.chat.id

    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return

    try:
        data = await unlock_api.user_team(user.id)
    except ResponseException as ex:
        if ex.status_code == 404 and ex.has_reason:
            await bot.send_message(chat_id, messages.team_not_found)
            return
        else:
            await bot.send_message(message.chat.id, messages.error_message)
            raise ex
    except Exception as ex:
        await bot.send_message(message.chat.id, messages.error_message)
        raise ex

    tutor: User = models.User.get_or_none(id=data.tutor)

    await bot.send_message(chat_id, messages.team_message.format(name=data.name, score=round(data.balance, 1),
                                                                 tutor='' if tutor is None else f"{tutor.first_name} "
                                                                                                f"{tutor.last_name}"))

@dp.message_handler(filters.Text(equals=messages.qr_request))
async def qr_request(message: types.Message):
    chat_id = message.chat.id

    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return

    await bot.send_message(chat_id, messages.qr_code_view, reply_markup=km.getQRViewKeyboard())

@dp.message_handler(IsAdmin(), filters.Text(equals=messages.turn_on_admin))
async def turn_on_admin_button(message: types.Message):
    chat_id = message.chat.id
    try:
        user: models.User = models.User.get(models.User.chat_id == chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
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
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return
    user.admin_mode = False
    user.save()
    await bot.send_message(user.chat_id, messages.admin_mode.format(state="Выключен"),
                           reply_markup=km.getMainKeyboard(user))


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.broadcast))
async def broadcast_button(message: types.Message):
    await UserState.admin_broadcast.set()
    await bot.send_message(message.chat.id, messages.enter_text_to_broadcast_message)


@dp.message_handler(IsAdmin(), filters.Text(equals=messages.back))
async def back_button(message: types.Message):
    chat_id = message.chat.id
    try:
        user = models.User.get(chat_id=chat_id)
    except:
        await bot.send_message(chat_id, messages.not_met.format(bot=settings.BOT_USERNAME))
        return
    await bot.send_message(message.chat.id, messages.ok_message,
                           reply_markup=km.getMainKeyboard(user))

@dp.message_handler(IsAdmin(), filters.Text(equals=messages.start_tunnel))
async def start_tunnel_button(message: types.Message, state: FSMContext):
    await state.set_state(UserState.opening_tunnel)
    await bot.send_message(message.chat.id, messages.choose_companion)

@dp.message_handler(IsAdmin(), state=UserState.opening_tunnel)
async def chose_tunnel_id(message: types.Message, state: FSMContext):
    s_user_id = message.text
    if s_user_id == "-1":
        await state.finish()
        return
    if not str.isdigit(s_user_id):
        await bot.send_message(message.chat.id, "Введите число")
        return

    companion: User | None = User.get_or_none(User.id == int(s_user_id))
    if companion is None:
        await bot.send_message(message.chat.id, "Собеседник не найден")
        return
    if companion.chat_id == message.chat.id:
        await bot.send_message(message.chat.id, "Вы не можете начать диалог с собой!")
        return
    admin_data = InTunnelData("Админ", companion.chat_id)
    participant_data = InTunnelData("Участник", message.chat.id)

    await state.set_state(UserState.in_tunnel)
    await state.set_data(admin_data.__dict__)
    await state.storage.set_state(chat=companion.chat_id, state=UserState.in_tunnel)
    await state.storage.set_data(chat=companion.chat_id, data=participant_data.__dict__)
    await bot.send_message(companion.chat_id, messages.tunnel_started.format(role="Админ"),
                           reply_markup=km.getTunnelKeyboard())
    await bot.send_message(message.chat.id, messages.tunnel_started.format(role="Участник"),
                           reply_markup=km.getTunnelKeyboard())
