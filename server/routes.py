from aiohttp import web

from schemas import *
from services import start_registration, start_voting, broadcast, start_question
from utils.models import Vote, Registration

routes = web.RouteTableDef()


@routes.post('/message/publish')
async def apiMessage(request: web.Request, data: BroadcastMessageRequest):
    await broadcast(data.message_text)
    return BroadcastMessageResponse(message_id=data.message_id)


@routes.post('/vote/publish')
async def apiVote(request: web.Request, data: BroadcastVoteRequest):
    if Vote.get_or_none(Vote.vote_id == data.vote_id) is not None:
        return ErrorResponse(reason=f'Vote with id {data.vote_id} is already exist')
    try:

        vote = Vote.create(vote_id=data.vote_id,
                           vote_text=data.vote_text,
                           options=list(map(dict, data.options)), message_id=0)
        msg_id = await start_voting(data.vote_id, data.vote_text, data.options)
        vote.message_id = msg_id
        vote.save()

    except Exception as ex:
        return ErrorResponse(reason=str(ex.args))
    return BroadcastVoteResponse(vote_id=data.vote_id)


@routes.post('/question/publish')
async def apiQuestion(request: web.Request, data: BroadcastQuestionRequest):
    await start_question(data.question_text, data.question_id)
    return BroadcastQuestionResponse(question_id=data.question_id)


@routes.post('/registration/publish')
async def apiRegistration(request: web.Request, data: BroadcastRegistrationRequest):
    if Registration.get_or_none(Registration.registration_id == data.registration_id) is not None:
        return ErrorResponse(reason=f'Registration with id {data.registration_id} is already exist')
    try:

        registration = Registration.create(registration_id=data.registration_id,
                                           registration_text=data.registration_text,
                                           options=list(map(dict, data.options)), message_id=0)
        msg_id = await start_registration(data.registration_id, data.registration_text, data.options)
        registration.message_id = msg_id
        registration.save()

    except Exception as ex:
        return ErrorResponse(reason=str(ex.args))
    return BroadcastRegistrationResponse(registration_id=data.registration_id)


@routes.post('/registration/update')
async def apiRegistration(request: web.Request, data: UpdateRegistrationRequest):
    return UpdateRegistrationResponse(registration_id=data.registration_id)
