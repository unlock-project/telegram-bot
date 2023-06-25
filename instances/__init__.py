from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from server import AppBundle
from utils import config
from utils.unlockapi import UnlockAPI

bot = Bot(token=config.getToken(), parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
unlock_api = UnlockAPI(config.getUnlockApiURL())
app = AppBundle()
