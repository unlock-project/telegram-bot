import logging
import aiohttp
import traceback

from utils import objects
from utils.objects import *
from utils.models import Vote, Choice, Question, Registration, Promocode, Option


class UnlockAPI:
    url = ''

    def __init__(self, url: str):
        self.url = url

    async def _get(self, function: str, params=None):
        if params is None:
            params = {}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(
                    self.url + function, params=params) as resp:
                data = await resp.text()

        try:
            json_data = json.loads(data)
        except:
            logging.error(f"Server returns non-json data url:{function}, params: {params}")
            return {"success": False}

        return json_data

    async def _post(self, function: str, body=None):
        if body is None:
            body = {}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(
                    self.url + function, data=json.dumps(body), headers={'content-type': 'application/json'}) as resp:
                data = await resp.text()

        try:
            json_data = json.loads(data)
        except:
            logging.error(f"Server returns non-json data url:{function}, data: {body}")
            return {"success": False}

        return json_data

    async def getUserById(self, id: int):
        data = await self._get("participant", {"id": id})

        return objects.getUserByJson(data)

    async def getScore(self, id: int):
        data = await self._get("score", {"id": id})
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

    async def update_db(self) -> bool:
        data = await self._get("bot/functions")
        Registration.delete().execute()
        Option.delete().execute()
        Promocode.delete().execute()
        Question.delete().execute()
        Vote.delete().execute()
        Choice.delete().execute()
        if "data" not in data.keys():
            return False
        for function in data["data"]:
            try:
                if function["TYPE"] == 1:  # promocode
                    promocode_model = Promocode.create(**function)
                    promocode_model.save()
                elif function["TYPE"] == 2:  # Question
                    question_mode = Question.create(**function)
                    question_mode.save()
                elif function["TYPE"] == 3:  # Vote
                    vote_model = Vote.create(**function)

                    vote_model.save()
                    for choice in function['choices']:
                        choice_model = Choice.create(vote=vote_model, name=choice)
                        choice_model.save()
                elif function["TYPE"] == 4:  # Registration
                    registration_model = Registration.create(**function)
                    registration_model.save()
                    for option in function['options']:
                        option_model = Option.create(**option, registration=registration_model)
                        option_model.save()
            except Exception as e:
                logging.error(traceback.format_exc())
                continue
        return True
