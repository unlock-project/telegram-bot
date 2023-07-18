import logging
import ssl

import aiogram
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web
from aiogram.dispatcher import Dispatcher

import instances
import utils.models
from utils.settings import WEBHOOK_PATH, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL, \
    API_PATH, SKIP_UPDATES
from .middleware import middleware
from utils.models import db

class AppBundle:

    def __init__(self):
        pass

    def run(self, bot: aiogram.Bot, dp: Dispatcher, routes):
        async def on_startup(app: web.Application, *args, **kwargs):
            await bot.set_webhook(WEBHOOK_URL)
            if SKIP_UPDATES:
                await dp.skip_updates()


        async def on_shutdown(*args, **kwargs):
            logging.warning('Shutting down..')

            # insert code here to run it before shutdown

            # Remove webhook (not acceptable in some cases)
            await bot.delete_webhook()

            # Close DB connection (if used)
            await dp.storage.close()
            await dp.storage.wait_closed()
            await instances.unlock_api.close()
            logging.warning('Bye!')

        app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
        # API Application
        api_app = web.Application()
        api_app.router.add_routes(routes)
        api_app.middlewares.append(middleware)
        # Setup event handlers.
        app.on_startup.append(on_startup)
        app.on_startup.append(utils.models.connect)
        app.on_shutdown.append(on_shutdown)
        # Setup API app
        app.add_subapp(API_PATH, api_app)
        # Generate SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
        # Start web-application.
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)
        # web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
