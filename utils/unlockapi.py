import enum

import aiohttp

from utils import objects
from utils.objects import *


class APIMethods(enum.Enum):
    REGISTER_USER = '/register/user'
    EVENTS_SCAN = '/events/scan'


class UnlockAPI:
    url = ''
    __session: aiohttp.ClientSession

    def __init__(self, url: str):
        self.url = url
        timout = aiohttp.ClientTimeout()
        self.__session = aiohttp.ClientSession(base_url=url, connector=aiohttp.TCPConnector(verify_ssl=False))

    async def _get(self, function: str, params=None):
        if params is None:
            params = {}
        try:
            async with self.__session.get(
                    function, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            return None

    async def _post(self, function: str, body=None):
        if body is None:
            body = {}
        async with self.__session.post(
                function, data=json.dumps(body), headers={'content-type': 'application/json'}) as resp:
            if resp.status == 200:
                return await resp.json()

    async def getUserById(self, id: int):
        data = await self._get("participant", {"id": id})

        return objects.getUserByJson(data)

    async def getScore(self, id: int):
        data = await self._get("score", {"id": id})
        if 'data' not in data:
            return None
        return data['data']['score']

    async def getDaily(self, id: int):
        data = await self._get("today", {"id": id})
        return data

    async def sendUserData(self, username: str, deeplink: str):
        data = await self._get("/bot/id", {"username": username if username is not None else "", "deeplink": deeplink})
        return data

    async def sendRegistration(self, user_id: int, registration_id: int, option: str):
        data = await self._post("bot/answer/", {"id": user_id, "function_id": registration_id, "answer": option,
                                                "type": 4})
        return data

    async def sendVoteChoice(self, user_id: int, vote_id: int, choice: str):
        data = await self._post("bot/answer/", {"id": user_id, "function_id": vote_id, "answer": choice,
                                                "type": 3})
        return data

    async def sendAnswer(self, user_id: int, question_id, answer: str):
        data = await self._post("bot/answer/", {"id": user_id, "function_id": question_id, "answer": answer,
                                                "type": 2})
        return data

    async def sendPromocode(self, user_id: int, code_id: str):
        # type 1
        data = await self._post("bot/answer/", {"id": user_id, "function_id": code_id, "type": 1})
        return data
        pass
