import asyncio
import json

import aiohttp
import pydantic
from unlockapi import schemas
from .methods import APIMethods


class UnlockAPI:
    url = ''
    __session: aiohttp.ClientSession


    def __init__(self, url: str):
        self.url = url
        self.__session = None

    async def _get(self, function: APIMethods, params=None):
        if not self.__session:
            self.__session = aiohttp.ClientSession(base_url=self.url, connector=aiohttp.TCPConnector(verify_ssl=False))
        if params is None:
            params = {}
        try:
            async with self.__session.get(
                    function.value, params=params) as resp:
                if resp.status == 200:
                    if resp.content_type != 'application/json':
                        raise TypeError(f"Non-json response ({resp.content_type}) in function {function.value}")
                    return await resp.json()
                else:
                    raise TypeError(f"Response status {resp.status} in function {function.value}")
        except:
            return None

    async def _post(self, function: APIMethods, body: pydantic.BaseModel):
        if not self.__session:
            self.__session = aiohttp.ClientSession(base_url=self.url, connector=aiohttp.TCPConnector(verify_ssl=False))
        if body is None:
            body = {}
        async with self.__session.post(
                function.value, data=body.json(), headers={'content-type': 'application/json'}) as resp:
            if resp.status == 200:
                if resp.content_type != 'application/json':
                    raise TypeError(f"Non-json response ({resp.content_type}) in function {function.value}")
                return await resp.json()
            else:
                raise TypeError(f"Response status {resp.status} in function {function.value}")

    async def register_user(self, username: str):
        data = await self._post(APIMethods.REGISTER_USER, schemas.BotRegisterSchema(username=username))
        return schemas.UserSchema(**data)

    async def user_team(self, user_id: int):
        data = await self._get(APIMethods.USER_TEAM, {"user_id": user_id})
        return schemas.TeamSchema(**data)

    async def events_today(self, user_id: int):
        data = await self._get(APIMethods.EVENTS_TODAY, {"user_id": user_id})
        return [schemas.EventSchema(**event) for event in data]

    async def promo_activate(self, code: str, user_id: int, time: str):
        data = await self._post(APIMethods.PROMO_ACTIVATE, schemas.PromoBotSchema(code=code, user_id=user_id,
                                                                                  time=time))
        return schemas.PromoSchema(**data)

    async def question_answer(self, question_id: int, user_id: int, answer: str):
        data = await self._post(APIMethods.QUESTION_RESPONSE, schemas.AnswerBotSchema(question_id=question_id,
                                                                                      user_id=user_id, answer=answer))
        return schemas.MessageSchema(**data)

    async def registration_choose(self, registration_id: int, user_id: int, option_id: int):
        data = await self._post(APIMethods.REGISTRATION_RESPONSE, schemas.OptionBotSchema(registration_id=registration_id,
                                                                                          user_id=user_id,
                                                                                          option_id=option_id))
        return schemas.RegistrationSchema(**data)

    async def vote_choose(self, vote_id: int, user_id: int, option_id: int):
        data = await self._post(APIMethods.VOTE_RESPONSE, schemas.ChoiceBotSchema(vote_id=vote_id, user_id=user_id,
                                                                                  option_id=option_id))
        return schemas.MessageSchema(**data)

    async def close(self):
        await self.__session.close()