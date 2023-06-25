from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    entering_promocode = State()
    admin_broadcast = State()
    answering_question = State()