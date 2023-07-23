import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv("dev.env")

# telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPER_ADMIN = int(os.getenv('SUPER_ADMIN', '313961073'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
BOT_USERNAME = ""
SKIP_UPDATES = bool(int(os.getenv('SKIP_UPDATES', '0')))
# Unlock api
UNLOCK_API_URL = os.getenv('UNLOCK_API_URL')
# webhook settings
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = '/bot/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBHOOK_SSL_CERT = './server/certs/fullchain.pem'
WEBHOOK_SSL_PRIV = './server/certs/privkey.pem'
API_PATH = '/api/'
# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', '8001'))
# Postgres settings
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'unlockbot')

BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_PATH = BASE_DIR / 'logs'