import enum


class APIMethods(enum.Enum):
    REGISTER_USER = '/api/users/register'
    USER_TEAM = '/api/users/team'
    EVENTS_TODAY = '/api/events/today'
    PROMO_ACTIVATE = '/bot/api/promo/activate'
    QUESTION_RESPONSE = '/bot/api/question/response'
    REGISTRATION_RESPONSE = '/bot/api/registration/response'
    VOTE_RESPONSE = '/bot/api/vote/response'
    USER_BALANCE = '/api/users/balance'
    REPORT = '/bot/api/report'