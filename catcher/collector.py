from collections import namedtuple
import sys
import time
import inspect

Report = namedtuple('Report', ['timestamp', 'exception', 'traceback'])
Frame = namedtuple('Frame', ['file', 'line', 'code', 'locals'])


def __collect_frame(frame, lineno):
    raw_sourcelines = inspect.getsourcelines(frame)
    if lineno - raw_sourcelines[1] > 6:
        start_line = lineno - 6
        offset = lineno - raw_sourcelines[1] - 6
    else:
        offset = 0
        start_line = raw_sourcelines[1]
    if len(raw_sourcelines[0]) - (lineno - raw_sourcelines[1]) > 6:
        end_index = (lineno - raw_sourcelines[1]) + 6
    else:
        end_index = len(raw_sourcelines[0])
    return Frame(
        file=inspect.getfile(frame),
        line=lineno,
        locals=frame.f_locals,
        code=([raw_sourcelines[0][i] for i in range(offset, end_index)], start_line),
    )


def backup(exception):
    exception.traceback_backup = sys.exc_info()[2]


def collect(exception):
    traceback = []

    if hasattr(exception, 'traceback_backup'):
        tb = exception.traceback_backup
    else:
        exc_info = sys.exc_info()
        tb = exc_info[2]
    if tb is None and hasattr(exception, "__traceback__"):
        tb = exception.__traceback__
    while tb:
        frame = tb.tb_frame
        traceback.append(__collect_frame(frame, tb.tb_lineno))
        tb = tb.tb_next

    return Report(
        timestamp=time.time(),
        exception=exception,
        traceback=traceback,
    )
