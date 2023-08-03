import asyncio
import datetime
import logging
import os.path

import aiogram

from handlers import callback_handler, message_handler, event_handler, error_handler, middlewares  # noqa: F401
from instances import bot, dp, app
from server.routes import routes
from utils.my_filters import IsAdmin
from utils import settings
from utils.settings import LOGS_PATH

dp.filters_factory.bind(IsAdmin)

if not os.path.exists(LOGS_PATH):
    os.mkdir(LOGS_PATH)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_PATH / f"log-{datetime.datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)

async def register_bot(_bot: aiogram.Bot):
    settings.BOT_USERNAME = (await _bot.get_me()).username

if __name__ == "__main__":
    asyncio.run(register_bot(bot))
    app.run(bot, dp, routes)

