# webhook settings
WEBHOOK_HOST = 'https://unlock.sumjest.ru'
WEBHOOK_PATH = '/bot/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBHOOK_SSL_CERT = './server/certs/fullchain1.pem'
WEBHOOK_SSL_PRIV = './server/certs/privkey1.pem'

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = 443