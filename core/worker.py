import os
import signal
import logging
import threading
from multiprocessing import Process, Queue, current_process, cpu_count
from _queue import Empty
from typing import Callable, Any, Optional

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 0.5


class TaskWorker:
    """Задание для обработки воркером"""

    __slots__ = ('func', 'args', 'timeout')

    def __init__(self, func: Callable[..., float], args=(), timeout=DEFAULT_TIMEOUT):
        self.func = func  # todo class taskresult (внутри намерения)
        self.args = args
        self.timeout = timeout


class Workers:
    """
    Класс для управления воркерами.

    >>> def func():
    ...     return 42
    ...
    >>> workers = Workers()
    >>> workers.start()
    >>> workers.add_task(TaskWorker(func))
    >>> print(workers.get_result())
    42
    >>> workers.stop()
    """

    __slots__ = ('__q_in', '__q_out')

    def __init__(self):
        self.__q_in = Queue()
        self.__q_out = Queue()

    def start(self):
        for i in range(cpu_count()):
            start_worker(self.__q_in, self.__q_out)

    def stop(self):
        for i in range(cpu_count() * 2):  # на всякий случай
            self.__q_in.put(None)

    def add_task(self, task: TaskWorker):
        self.__q_in.put(task, block=True)

    def get_result(self, timeout=DEFAULT_TIMEOUT) -> Optional[Any]:
        try:
            return self.__q_out.get(block=True, timeout=timeout + 0.05)
        except Empty:
            return None


def start_worker(q_in: Queue, q_out: Queue):
    Process(target=process_worker, args=(q_in, q_out)).start()


def process_worker(q_in: Queue, q_out: Queue):
    process_name = current_process().name
    log.info('%s ready', process_name)

    def kill_self():
        start_worker(q_in, q_out)
        log.error('worker will kill by timeout')
        os.kill(os.getpid(), signal.SIGKILL)

    for task in iter(q_in.get, None):
        log.debug('%s %s%s', process_name, task.func.__name__, task.args)
        watchdog = threading.Timer(task.timeout, kill_self)
        watchdog.start()
        result = None
        try:
            result = task.func(*task.args)
        except BaseException:
            log.exception('')
        watchdog.cancel()
        q_out.put(result)

    log.info('%s shutdown', process_name)
