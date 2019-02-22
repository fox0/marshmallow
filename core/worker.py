import os
import signal
import logging
import threading
from multiprocessing import Process, Queue, current_process, cpu_count
from _queue import Empty
from typing import Any, Optional

from core.luna import LunaCode

log = logging.getLogger(__name__)

# для чтения из очереди
DEFAULT_TIMEOUT = 60


class Workers:
    __slots__ = ('__q_in', '__q_out')

    def __init__(self):
        self.__q_in = Queue()  # todo очередь с приоритетами
        self.__q_out = Queue()

    def start(self):
        for i in range(cpu_count()):
            start_worker(self.__q_in, self.__q_out)

    def stop(self):
        for i in range(cpu_count() * 2):  # на всякий случай
            self.__q_in.put(None)

    def append(self, luna: LunaCode, bot_state: dict):
        self.__q_in.put((luna, bot_state), block=True)

    def get_result(self, timeout=DEFAULT_TIMEOUT) -> Optional[Any]:
        try:
            return self.__q_out.get(block=True, timeout=timeout + 0.05)
        except Empty:
            return None


def start_worker(q_in: Queue, q_out: Queue):
    Process(target=process_worker, args=(q_in, q_out)).start()


def process_worker(q_in: Queue, q_out: Queue):
    """Процесс-воркер"""
    process_name = current_process().name
    log.info('%s ready', process_name)

    def kill_self():
        start_worker(q_in, q_out)
        log.error('worker will kill by timeout')
        os.kill(os.getpid(), signal.SIGKILL)

    for luna, bot_state in iter(q_in.get, None):
        assert isinstance(luna, LunaCode)
        # todo bot_state??????

        log.debug('%s run %s', process_name, luna)
        watchdog = threading.Timer(luna.timeout, kill_self)
        watchdog.start()
        result = None
        try:
            luna.execute()
            result, internal_state = luna.globals.main(bot_state)
            #     # абстракции протекают
            #     return list(result), dict(internal_state)
            #
            # result = task.func(*task.args)
            result = list(result), dict(internal_state)
        except BaseException:
            log.exception('')
        watchdog.cancel()
        q_out.put(result)

    log.info('%s shutdown', process_name)
