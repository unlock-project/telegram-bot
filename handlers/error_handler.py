import asyncio
import json
import logging
import traceback
from typing import Any

from aiogram.types import Update, Message

from instances import dp
from services.services import log_error


class MessageEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Message):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


@dp.errors_handler()
async def all_handler(update: Update, error: Exception):
    logging.error(traceback.format_exc())
    try:
        asyncio.get_running_loop().create_task(log_error(error, update))
    except:
        logging.error(traceback.format_exc())
    return True

