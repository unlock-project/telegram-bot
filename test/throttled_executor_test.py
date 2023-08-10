import asyncio
import unittest
from typing import Union

from lib.function_wrapper import supervised
from lib.latest_throttled_executor import ThrottledTask, RetryAfterException, LatestThrottledExecutor

TRACKER_EXPECTED_RESULT = "aboba"


class Tracker:
    result: Union[str, None]
    attempts: int

    def __init__(self):
        self.result = None
        self.attempts = 0


@supervised
async def success(tracker: Tracker, delay_millis: int = 0):
    await asyncio.sleep(delay_millis / 1000)
    tracker.attempts += 1
    tracker.result = TRACKER_EXPECTED_RESULT


@supervised
async def error(delay_millis: int = 0):
    await asyncio.sleep(delay_millis / 1000)
    raise RuntimeError("Some error")


@supervised
async def retry_after(
        tracker: Tracker,
        retry_after_millis: int,
        attempts: int,
        delay_millis: int = 0
):
    tracker.attempts += 1
    await asyncio.sleep(delay_millis / 1000)

    if tracker.attempts == attempts:
        tracker.result = TRACKER_EXPECTED_RESULT
    else:
        raise RetryAfterException(retry_after_millis)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class TestThrottledTask(unittest.IsolatedAsyncioTestCase):

    def assertRun(self, task: ThrottledTask, attempts: int = 1):
        self.assertEqual(True, task.done())
        self.assertEqual(attempts, task.attempts())
        self.assertEqual(0, task.next_attempt())

    def assertSuccess(self, task: ThrottledTask, tracker: Tracker):
        self.assertRun(task)
        self.assertEqual(None, task.latest_error())
        self.assertEqual(TRACKER_EXPECTED_RESULT, tracker.result)

    def assertError(self, task: ThrottledTask):
        self.assertRun(task)
        self.assertIsInstance(task.latest_error(), RuntimeError)

    async def test_success(self):
        tracker = Tracker()
        task = ThrottledTask(success(tracker))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1)
        self.assertSuccess(task, tracker)

    async def test_success_delayed(self):
        tracker = Tracker()
        task = ThrottledTask(success(tracker, 200))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1)
        self.assertSuccess(task, tracker)

    async def test_error(self):
        task = ThrottledTask(error())
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1)
        self.assertError(task)

    async def test_error_delayed(self):
        task = ThrottledTask(error(200))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1)
        self.assertError(task)

    async def test_retry_after(self):
        tracker = Tracker()
        task = ThrottledTask(retry_after(tracker, 200, attempts=3))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1)
        self.assertRun(task, 3)

    async def test_retry_after_delayed(self):
        tracker = Tracker()
        task = ThrottledTask(retry_after(tracker, 200, attempts=3, delay_millis=200))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(2)
        self.assertRun(task, 3)

    async def test_cancel(self):
        tracker = Tracker()
        task = ThrottledTask(retry_after(tracker, 10000, attempts=2))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1)
        task.cancel()

        self.assertEqual(False, task.done())
        self.assertEqual(2, task.attempts())
        self.assertEqual(10000, task.next_attempt())

    async def test_next_attempt(self):
        tracker = Tracker()
        task = ThrottledTask(retry_after(tracker, 2000, attempts=3))
        task.schedule(asyncio.get_running_loop())
        await asyncio.sleep(1.5)
        task.cancel()
        self.assertGreater(1000, task.next_attempt())
        self.assertGreater(task.next_attempt(), 0)


class TestLatestThrottledExecutor(unittest.IsolatedAsyncioTestCase):

    def assertRun(self, tracker: Tracker, attempts: int = 1):
        self.assertEqual(attempts, tracker.attempts)
        self.assertEqual(TRACKER_EXPECTED_RESULT, tracker.result)

    def assertNotRun(self, tracker: Tracker, attempts: int = 1):
        self.assertEqual(attempts, tracker.attempts)
        self.assertNotEqual(TRACKER_EXPECTED_RESULT, tracker.result)

    async def test_success(self):
        tracker = Tracker()
        executor = LatestThrottledExecutor(asyncio.get_event_loop())
        executor.enqueue(success(tracker), "my_task")
        await asyncio.sleep(1)
        self.assertRun(tracker)

    async def test_retry_after(self):
        tracker = Tracker()
        executor = LatestThrottledExecutor(asyncio.get_event_loop())
        executor.enqueue(retry_after(tracker, 200, attempts=3), "my_task")
        await asyncio.sleep(2)
        self.assertRun(tracker, 3)

    async def test_multiple(self):
        tracker1 = Tracker()
        tracker2 = Tracker()
        tracker3 = Tracker()
        executor = LatestThrottledExecutor(asyncio.get_event_loop())

        executor.enqueue(retry_after(tracker1, 500, attempts=3, delay_millis=2000), "my_task")
        await asyncio.sleep(1)
        executor.enqueue(retry_after(tracker2, 500, attempts=3), "my_task")
        await asyncio.sleep(1)
        executor.enqueue(retry_after(tracker3, 500, attempts=3), "my_task")
        await asyncio.sleep(2)

        self.assertNotRun(tracker1, 1)
        self.assertNotRun(tracker2, 2)
        self.assertRun(tracker3, 3)


if __name__ == "__main__":
    unittest.main()
