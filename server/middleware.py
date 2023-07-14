import inspect
import logging
import traceback

import aiohttp.web
from aiohttp.web import middleware
from pydantic import BaseModel

from schemas import ErrorResponse
from utils.settings import API_PATH


@middleware
async def middleware(request: aiohttp.web.Request, handler):

    url_path = request.url.path
    if not url_path.startswith(API_PATH):
        return await handler(request)
    arg_spec = inspect.getfullargspec(handler)
    if request.method == 'POST':
        if 'data' not in arg_spec.annotations.keys():
            return await handler(request)

        data_class = arg_spec.annotations['data']
        if not issubclass(data_class, BaseModel):
            return await handler(request)
        try:
            data = await request.json()
        except:
            return aiohttp.web.json_response(ErrorResponse(reason='Bad json data').dict())
        try:
            validated = data_class(**data)
        except:
            logging.error(traceback.format_exc())
            return aiohttp.web.json_response(ErrorResponse(reason='Bad request').dict())
        try:
            resp = await handler(request, validated)
        except Exception as ex:
            return aiohttp.web.json_response(ErrorResponse(reason=f'{type(ex).__name__}: {str(ex)}').dict())
        if not issubclass(type(resp), BaseModel):
            logging.error('API response is not a pydantic class')
            return aiohttp.web.json_response({}, status=500)
        return aiohttp.web.json_response(resp.dict())
    elif request.method == "GET":
        try:
            resp = await handler(request, **request.query)
            if not issubclass(type(resp), BaseModel):
                logging.error('API response is not a pydantic class')
                return aiohttp.web.json_response({}, status=500)
            return aiohttp.web.json_response(resp.dict())
        except Exception as ex:
            logging.error(traceback.format_exc())
            return aiohttp.web.json_response(ErrorResponse(reason=f"{type(ex).__name__}: {str(ex)}").dict())
    else:
        return await handler(request)

