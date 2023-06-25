import asyncio
import logging
import traceback

from aiohttp import web

from instances import bot
from server import ErrorResponse, SuccessResponse

routes = web.RouteTableDef()


@routes.post('/api/sendmessage')
async def apiMessage(request: web.Request):
    if request.content_type != 'application/json':
        return ErrorResponse('non-json data')
    try:
        body = await request.json()
        if 'chat_id' not in body or 'message' not in body:
            return ErrorResponse('has no expected data')
        chat_id = int(body['chat_id'])
        message = body['message']
        message_id = (await bot.send_message(chat_id, message)).message_id
    except Exception as ex:
        return ErrorResponse(ex.args)
    return SuccessResponse({'message': message, 'message_id': message_id})


@routes.post('/api/broadcast')
async def apiMessage(request: web.Request):
    if request.content_type != 'application/json':
        return ErrorResponse('non-json data')
    try:
        body = await request.json()
        if 'chat_ids' not in body or 'message' not in body:
            return ErrorResponse('has no expected data')
        chat_ids = map(int, body['chat_ids'])
        message = body['message']
        for chat_id in chat_ids:
            await asyncio.sleep(0.040)  # not more than 30 per second (25)
            try:
                await bot.send_message(chat_id, message)
            except:
                logging.error(traceback.format_exc())
                logging.error(chat_id)
    except Exception as ex:
        return ErrorResponse(ex.args)
    return SuccessResponse({'message': message})
