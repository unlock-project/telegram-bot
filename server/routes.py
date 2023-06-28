from aiohttp import web

from schemas import *

routes = web.RouteTableDef()


@routes.post('/message/publish')
async def apiMessage(request: web.Request, data: BroadcastMessageRequest):
    return BroadcastMessageResponse(message_id=data.message_id)


@routes.post('/vote/publish')
async def apiVote(request: web.Request, data: BroadcastVoteRequest):
    return BroadcastVoteResponse(vote_id=data.vote_id)


@routes.post('/question/publish')
async def apiQuestion(request: web.Request, data: BroadcastQuestionRequest):
    return BroadcastQuestionResponse(question_id=data.question_id)


@routes.post('/registration/publish')
async def apiRegistration(request: web.Request, data: BroadcastRegistrationRequest):
    return BroadcastRegistrationResponse(registration_id=data.registration_id)


@routes.post('/registration/update')
async def apiRegistration(request: web.Request, data: UpdateRegistrationRequest):
    return UpdateRegistrationResponse(registration_id=data.registration_id)
