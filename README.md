
# 🤖 Unlock bot v2  
  
Greetings in the repository unlockbot v2. This is an asynchronous bot running on the [aiogram v2](https://github.com/aiogram/aiogram)  
framework. Bot working on webhooks and have simple aiohttp web server for listening request from [backend](https://github.com/unlock-project/backend).  
  
  
## Project structure  
  
  
  
| Module name | Description |  
|-------------|-----------------------------------------------------------------------------------------------|  
| `catcher` | Fixed [catcher](https://github.com/Eugeny/catcher) module, which builds html page by traceback |  
| `handlers` | There is all telegram updates handlers |  
| `intances` | The main instances used in whole project, such as bot, dispatcher, unlockapi. |  
| `keyboard` | Keyboard generator |  
| `schemas` | Bot API schemas |  
| `server` | Main module, contains aiogram web application and api subapp |  
| `services` | Important bot functions |
| `states` | FSM module |
| `unlockapi` | UnlockAPI v2 module |
| `utils` | Mini modules |

## Environment variables  
  
| Variable | Default value | Description |  
|-------------------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|  
| `BOT_TOKEN` | !! REQUIRED !! | Telegram bot token. |  
| `SUPER_ADMIN` | `313961073` | Chat id of main bot admin (me). |  
| `CHANNEL_ID` | !! REQUIRED !! | Chat id of main bot channel. |  
| `SKIP_UPDATES` | `0` | Skip updates, which came where bot was offline. |  
| `UNLOCK_API_URL` | !! REQUIRED !! | URL of unlock api (backend). With `/` in the end! |  
| `WEBHOOK_HOST` | !! REQUIRED !! | url with HTTPS (important ssl!) of bot. Without `/` in the end! |  
| `WEBAPP_PORT` | `8001` | Local port that aiohttp will listen. |  
| `DB_HOST` | `localhost` | Database host. |
| `DB_PORT` | `5432` | Database port. |  
| `DB_USER` | `postgres` | Database user. | 
| `DB_PASS` | `postgres` | Database password. |  
| `DB_NAME` | `unlockbot` | Database name |


Example development config:  
  
```  
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
CHANNEL_ID=-1001981984707
UNLOCK_API_URL=https://api.example.com/
WEBHOOK_HOST=https://bot.example.com 
```  
  
## Development  
  
Follow the steps below in order to set up development environment.  
  
1. Install dependencies: `pip install -r requirements.txt`.  Install `psycopg2` instead of `psycopg2-binary`, second for docker.
2. Create `.env` at the root of the project and set required environment variables.  
3. Run own postgresql server
4. Run bot `python unlockbot.py`
  
## Deploy  
  
Follow the steps below in order to deploy the system using Docker.
1. Create `.env` at the root of the project and set required environment variables.
2. Run `docker build -t romaaaka/unlockbot:v{verison}-dev .`
3. Or if you want to pull image from docker hub go to step 5.
4. Change if you need image name in `docker-compose.yml` in `services->unlock-bot->image` to tag that you wrote in 2 step.
5. Run `docker-compose up -d`