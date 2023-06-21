import logging
import ssl
import typing

import aiogram
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import hdrs, web
from aiogram.dispatcher import Dispatcher
from .route import Route
from .settings import WEBHOOK_PATH, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL


class AppBundle:
    routes: typing.List[Route]

    def __init__(self):
        self.routes = []

    def get(self, path: str):
        def decorator(func: typing.Callable):
            self.routes.append(Route(hdrs.METH_GET, path, func))
            return func

        return decorator

    def post(self, path: str):
        def decorator(func: typing.Callable):
            self.routes.append(Route(hdrs.METH_POST, path, func))

        return decorator

    def run(self, bot: aiogram.Bot, dp: Dispatcher):
        async def on_startup(*args, **kwargs):
            await bot.set_webhook(WEBHOOK_URL)

        async def on_shutdown(*args, **kwargs):
            logging.warning('Shutting down..')

            # insert code here to run it before shutdown

            # Remove webhook (not acceptable in some cases)
            await bot.delete_webhook()

            # Close DB connection (if used)
            await dp.storage.close()
            await dp.storage.wait_closed()

            logging.warning('Bye!')

        app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)

        # Setup event handlers.
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        for route in self.routes:
            app.router.add_route(route.method, route.path, route.func)
        # Generate SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
        # Start web-application.
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=context)
