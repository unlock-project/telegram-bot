import datetime
import logging
import sentry_sdk

from handlers import callback_handler, message_handler, event_handler, error_handler  # noqa: F401
from instances import bot, dp, app
from server.routes import routes
from utils.my_filters import IsAdmin

dp.filters_factory.bind(IsAdmin)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/log-{datetime.datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    app.run(bot, dp, routes)

