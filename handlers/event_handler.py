from aiogram import types

from instances import dp


@dp.my_chat_member_handler()
async def my_member_event(event: types.ChatMemberUpdated):
    pass
