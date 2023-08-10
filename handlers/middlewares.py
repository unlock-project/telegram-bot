import asyncio

from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineQuery
from aiogram.utils.exceptions import Throttled

from utils import messages
from utils.models import User
from instances import dp
from utils.settings import RATE_LIMIT

class UserBannedMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        user = User.get_or_none(User.chat_id==message.from_user.id)
        if user and user.is_banned:
            raise CancelHandler

    async def on_process_callback_query(self, call: CallbackQuery, data: dict):
        user = User.get_or_none(User.chat_id==call.from_user.id)
        if user and user.is_banned:
            raise CancelHandler

    async def on_process_inline_query(self, query: InlineQuery, data: dict):
        user = User.get_or_none(User.chat_id==query.from_user.id)
        if user and user.is_banned:
            raise CancelHandler

class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        """
        This handler is called when dispatcher receives a message

        :param message:
        """
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await message.reply(messages.throttled)

            # Cancel current handler
            raise CancelHandler()

    async def on_process_callback_query(self, callback_query: CallbackQuery, data: dict):
        """
        This handler is called when dispatcher receives a message

        :param callback_query:
        """
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_callback_query"

        # Use Dispatcher.throttle method.
        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await callback_query.answer(messages.throttled)

            # Cancel current handler
            raise CancelHandler()


dp.middleware.setup(UserBannedMiddleware())
dp.middleware.setup(ThrottlingMiddleware())