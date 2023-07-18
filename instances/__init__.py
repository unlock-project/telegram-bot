from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from server import AppBundle
from utils.settings import BOT_TOKEN, UNLOCK_API_URL
from unlockapi import UnlockAPI

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
unlock_api = UnlockAPI(UNLOCK_API_URL)
app = AppBundle()

__all__ = ['bot', 'storage', 'dp', 'unlock_api', 'app']
