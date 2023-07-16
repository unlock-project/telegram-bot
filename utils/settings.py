import os

# telegram
from pathlib import Path

BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPER_ADMIN = int(os.getenv('SUPER_ADMIN'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
BOT_USERNAME = 'lkunlock_bot'
# Unlock api
UNLOCK_API_URL = 'https://cdm.sumjest.ru/'
# webhook settings
WEBHOOK_HOST = 'https://unlock.sumjest.ru'
WEBHOOK_PATH = '/bot/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBHOOK_SSL_CERT = './server/certs/fullchain1.pem'
WEBHOOK_SSL_PRIV = './server/certs/privkey1.pem'
API_PATH = '/api/'
# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 8001
# Postgres settings
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_PATH = BASE_DIR / 'logs'
