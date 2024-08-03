import typing

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from lib.latest_throttled_executor import LatestThrottledExecutor
from server import AppBundle
from utils.settings import BOT_TOKEN, UNLOCK_API_URL, UNLOCK_API_TOKEN
from unlockapi import UnlockAPI

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
unlock_api = UnlockAPI(UNLOCK_API_URL, UNLOCK_API_TOKEN)
app = AppBundle()
latest_throttled_executor: typing.Optional[LatestThrottledExecutor] = None

__all__ = ['bot', 'storage', 'dp', 'unlock_api', 'app', 'latest_throttled_executor']
