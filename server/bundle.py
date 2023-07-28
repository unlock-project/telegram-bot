import logging

import aiogram
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

import instances
from utils.models import connect, cleanup
from utils.settings import WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL, \
    API_PATH, SKIP_UPDATES
from .middleware import middleware


class AppBundle:

    def __init__(self):
        pass

    def run(self, bot: aiogram.Bot, dp: Dispatcher, routes):
        async def on_startup(*args, **kwargs):
            if SKIP_UPDATES:
                logging.info("Skipping updates")
                await dp.skip_updates()
            logging.info("Setting webhook")
            result = await bot.set_webhook(WEBHOOK_URL)
            if result:
                logging.info("Webhook set")
            else:
                logging.critical("Webhook didn't set")

        async def on_shutdown(*args, **kwargs):
            logging.warning('Shutting down..')
            # Remove webhook (not acceptable in some cases)
            await bot.delete_webhook()

            # Close DB connection (if used)
            await dp.storage.close()
            await dp.storage.wait_closed()
            await instances.unlock_api.close()
            await bot.close()
            logging.warning('Bye!')

        app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
        # API Application
        api_app = web.Application()
        api_app.router.add_routes(routes)
        api_app.middlewares.append(middleware)
        # Setup event handlers.
        app.on_startup.append(connect)
        app.on_startup.append(on_startup)
        app.on_cleanup.append(cleanup)
        app.on_shutdown.append(on_shutdown)
        # Setup API app
        app.add_subapp(API_PATH, api_app)
        # Generate SSL context
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
        # Start web-application.
        # web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)

        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # sock.bind((WEBAPP_HOST, 0))
        # print(sock.getsockname()[1])

        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

