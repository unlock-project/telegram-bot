import datetime
import json
import typing


class APIUser:
    """
    date format: YYYY-MM-DD
    """
    id: int
    firstName: str
    lastName: str
    email: str
    dateOfBirth: str
    emailVerified: bool
    signUpDate: str

    def __init__(self):
        pass


class User:
    chat_id: int
    is_admin: bool
    admin_mode: bool
    id: int

    def __init__(self, chat_id, id: int, is_admin=False, admin_mode=False):
        self.chat_id = chat_id
        self.is_admin = is_admin
        self.admin_mode = admin_mode
        self.id = id

    def __str__(self):
        return f"({self.chat_id},{self.id} ,{self.is_admin}, {self.admin_mode})"


class APIVote:
    id: int
    title: str
    choices: typing.List[str]
    time: datetime.datetime

    def __init__(self, id: int, title: str, choices: typing.List[str], time: str, date: str, **kwargs):
        self.id = id
        self.title = title
        self.choices = choices
        self.time = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

    def __to_dict(self):
        data = self.__dict__
        data['time'] = self.time.timestamp()
        data['choices'] = json.dumps(data['choices'])
        return data


class APIQuestion:
    id: int
    title: str
    text: str
    time: datetime.datetime

    def __init__(self, id: int, title: str, text: str, time: str, date: str, **kwargs):
        self.id = id
        self.title = title
        self.text = text
        self.time = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

    def __to_dict(self):
        data = self.__dict__
        data['time'] = self.time.timestamp()
        return data


class APIPromocode:
    id: int
    title: str
    code: str
    answer: str
    photo: str
    time: datetime.datetime

    def __init__(self, id: int, title: str, code: str, answer: str, photo: str, time: str, date: str, **kwargs):
        self.id = id
        self.title = title
        self.code = code
        self.answer = answer
        self.photo = photo
        self.time = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

    def __to_dict(self):
        data = self.__dict__
        data['time'] = self.time.timestamp()
        return data


class APIRegistrationOption:
    title: str
    count: int
    max: int

    def __init__(self, title: str, count: int, max: int, **kwargs):
        self.title = title
        self.count = count
        self.max = max

    def __to_dict(self):
        return self.__dict__


class APIRegistration:
    id: int
    title: str
    text: str
    options: typing.List[APIRegistrationOption]
    time: datetime.datetime

    def __init__(self, id: int, title: str, text: str, options: typing.List[typing.Dict[str, typing.Union[str, int]]],
                 time: str, date: str, **kwargs):
        self.id = id
        self.title = title
        self.text = text
        self.options = []
        for option in options:
            self.options.append(APIRegistrationOption(option["title"], option["count"], option["max"]))
        self.time = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")


def getAPIUserByJson(json_data: str) -> APIUser:
    data: dict = json.loads(json_data)
    user = APIUser()
    for key in data.keys():
        setattr(user, key, data[key])
    return user
