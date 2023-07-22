import enum


class APIMethods(enum.Enum):
    REGISTER_USER = '/api/register/user'
    USER_TEAM = '/api/team/user'
    EVENTS_TODAY = '/api/events/today'
    PROMO_ACTIVATE = '/api/promo/activate'
    QUESTION_RESPONSE = '/api/question/response'
    REGISTRATION_RESPONSE = '/api/question/response'
    VOTE_RESPONSE = '/api/vote/response'