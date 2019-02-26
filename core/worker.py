import os
import signal
import logging
import threading
from multiprocessing import Process, Queue, current_process, cpu_count
from multiprocessing.managers import SyncManager
from queue import PriorityQueue
from _queue import Empty as QueueEmpty
from typing import Tuple, List, Dict

from core.luna import LunaCode, table2list, table2dict

log = logging.getLogger(__name__)


class MySyncManager(SyncManager):
    pass


MySyncManager.register('PriorityQueue', PriorityQueue)


class Workers:
    __slots__ = ('__q_in', '__q_out')

    def __init__(self):
        m = MySyncManager()
        m.start()
        # noinspection PyUnresolvedReferences
        self.__q_in = m.PriorityQueue()
        self.__q_out = Queue()

    def start(self):
        for i in range(cpu_count()):
            start_worker(self.__q_in, self.__q_out)

    def stop(self):
        for i in range(cpu_count()):
            self.__q_in.put((0, None))

    def append(self, luna: LunaCode, bot_state: dict):
        # очередь с приоритетами
        self.__q_in.put((luna.priority, (luna, bot_state)), block=True)

    def get_result(self) -> Tuple[List, Dict]:
        try:
            return self.__q_out.get(block=True)  # , timeout=timeout + 0.05)
        except QueueEmpty:
            # todo как-то пробрасывать код ошибки выше
            return [], {}


def start_worker(q_in: PriorityQueue, q_out: Queue):
    Process(target=process_worker, args=(q_in, q_out)).start()


def process_worker(q_in: PriorityQueue, q_out: Queue):
    """Процесс-воркер"""
    process_name = current_process().name
    log.info('%s ready', process_name)

    def kill_self():
        start_worker(q_in, q_out)
        log.error('worker will kill by timeout')
        os.kill(os.getpid(), signal.SIGKILL)

    while True:
        _, item = q_in.get()
        if item is None:
            break

        luna, bot_state = item
        assert isinstance(luna, LunaCode)
        log.debug('%s run %s', process_name, luna)
        watchdog = threading.Timer(luna.timeout, kill_self)
        watchdog.start()
        result, internal_state = [], {}
        # noinspection PyBroadException
        try:
            luna.execute()
            result, internal_state = luna.globals.main(bot_state)
        except BaseException:
            log.exception('')
            # todo как-то пробрасывать код ошибки выше
        watchdog.cancel()
        q_out.put((table2list(result), table2dict(internal_state)))

    log.info('%s shutdown', process_name)
