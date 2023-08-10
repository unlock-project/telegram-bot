import inspect
from functools import wraps
from typing import Callable, Final, Coroutine, Any


class AsyncFunction:
    __func: Final[Callable]
    __args: Final[tuple]
    __kwargs: Final[dict]

    def __init__(self, func: Callable, args: tuple, kwargs: dict):
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def get_coroutine(self) -> Coroutine:
        return self.__func(*self.__args, **self.__kwargs)


def supervised(func: Callable) -> Callable[..., AsyncFunction]:
    if not inspect.iscoroutinefunction(func):
        raise RuntimeError("The @supervised decorator can only be applied to async functions")

    @wraps(func)
    def wrapper(*args, **kwargs) -> AsyncFunction:
        return AsyncFunction(func, args, kwargs)

    return wrapper
