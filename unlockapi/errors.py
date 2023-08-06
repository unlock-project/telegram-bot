import asyncio
import json
import typing

from aiohttp import ClientResponse
from schemas import ErrorResponse

class ResponseException(Exception):
    status_code: int
    has_reason: bool
    reason: str
    response: ClientResponse

    def __init__(self, response: ClientResponse, data: typing.Optional[bytes] = None):
        self.response = response
        self.status_code = response.status
        self.has_reason = False
        if data:
            try:

                data = json.loads(data)
                error_response = ErrorResponse(**data)
                self.has_reason = True
                self.reason = error_response.reason
            except:
                pass

    def __str__(self):
        return (f"'{self.response.url}' returned {self.status_code}."
                f"{(' Reason: ' + self.reason) if self.has_reason else ''}")
    def __repr__(self):
            return str(self)