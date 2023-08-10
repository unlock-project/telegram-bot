import asyncio
import time
from asyncio import Task, AbstractEventLoop
from typing import Hashable, Union

from lib.function_wrapper import AsyncFunction


class RetryAfterException(BaseException):
    millis: int

    def __init__(self, millis: int):
        self.millis = millis


class ThrottledTask:
    __retry_after_millis: int
    __func: AsyncFunction

    __error: Union[BaseException, None]
    __done: bool
    __exec_loop: AbstractEventLoop
    __exec_task: Union[Task, None]
    __attempts: int
    __time_started: float

    def __init__(self, func: AsyncFunction, retry_after_millis: int = 0):
        self.__retry_after_millis = retry_after_millis
        self.__func = func
        self.__time_started = time.time()

        self.__error = None
        self.__done = False
        self.__exec_task = None
        self.__attempts = 0

    def schedule(self, loop: AbstractEventLoop):
        self.__done = False
        self.__exec_loop = loop
        self.__attempts += 1
        self.__exec_task = loop.create_task(self.__execute())

    def cancel(self):
        if self.__exec_task is None:
            return
        else:
            self.__exec_task.cancel()
            self.__done = True

    def done(self):
        return self.__done

    def latest_error(self):
        return self.__error

    def attempts(self):
        return self.__attempts

    def next_attempt(self):
        elapsed = time.time() - self.__time_started
        return max(self.__retry_after_millis - elapsed * 1000, 0)

    async def __execute(self):
        self.__time_started = time.time()
        await asyncio.sleep(self.__retry_after_millis / 1000)

        try:
            running_job = self.__exec_loop.create_task(self.__func.get_coroutine())
            await running_job
            self.__retry_after_millis = 0
            self.__done = True
            self.__error = None
            self.__exec_task = None

        except RetryAfterException as e:
            self.__error = e
            self.__retry_after_millis = e.millis
            self.schedule(self.__exec_loop)

        except BaseException as e:
            self.__error = e
            self.__done = True
            self.__exec_task = None


class LatestThrottledExecutor:
    __loop: AbstractEventLoop
    __tasks: dict[Hashable, ThrottledTask]

    def __init__(self, loop: AbstractEventLoop):
        self.__loop = loop
        self.__tasks = dict()

    def enqueue(self, func: AsyncFunction, task_uid: Hashable):
        initial_retry_after = 0

        if task_uid in self.__tasks:
            existing_task = self.__tasks[task_uid]
            existing_task.cancel()
            initial_retry_after = existing_task.next_attempt()

        new_task = ThrottledTask(func, initial_retry_after)
        self.__tasks[task_uid] = new_task
        new_task.schedule(self.__loop)
