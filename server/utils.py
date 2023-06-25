from aiohttp import web


def ErrorResponse(reason: str):
    return web.json_response({'ok': False, 'reason': reason}, status=400)


def SuccessResponse(result: dict):
    return web.json_response({'ok': True, 'result': result})
