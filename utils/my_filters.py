import json
import logging

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from utils.models import User


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        chat_id = message.chat.id
        try:
            user = User.get((User.chat_id == chat_id))
        except Exception as e:
            logging.info(e.args)
            return False
        return user.is_admin


class CallbackType(BoundFilter):
    callback_type: str

    def __init__(self, callback_type: str):
        self.callback_type = callback_type

    async def check(self, callback: types.CallbackQuery) -> bool:
        try:
            data = json.loads(callback.data)
            return data['type'] == self.callback_type
        except:
            return False
