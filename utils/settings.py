# telegram
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
SUPER_ADMIN = int(os.getenv('SUPER_ADMIN'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
# Unlock api
UNLOCK_API_URL = 'https://cw65021-django-wvkb6.tw1.ru/'
# webhook settings
WEBHOOK_HOST = 'https://unlock.sumjest.ru'
WEBHOOK_PATH = '/bot/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBHOOK_SSL_CERT = './server/certs/fullchain1.pem'
WEBHOOK_SSL_PRIV = './server/certs/privkey1.pem'
API_PATH = '/api/'

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 443