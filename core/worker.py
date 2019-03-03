"""
Многопроцессорные воркеры и всё что с ними связано
"""
#  Copyright (c) 2019. fox0 https://github.com/fox0/

import logging
import os
import signal
import threading
from _queue import Empty as QueueEmpty
from multiprocessing import Process, Queue, current_process, cpu_count
from multiprocessing.managers import SyncManager
from queue import PriorityQueue
from typing import Tuple, List, Dict

from core.luna import LunaCode, table2list, table2dict

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class MySyncManager(SyncManager):  # pylint: disable=missing-docstring
    pass


MySyncManager.register('PriorityQueue', PriorityQueue)  # pylint: disable=no-member


class Workers:
    """Класс для управления процессами-воркерами"""
    __slots__ = ('__count_workers', '__q_in', '__q_out')

    def __init__(self, count_workers=cpu_count()):
        self.__count_workers = count_workers
        manager = MySyncManager()
        manager.start()
        # noinspection PyUnresolvedReferences
        self.__q_in = manager.PriorityQueue()  # pylint: disable=no-member
        self.__q_out = Queue()

    def start(self):
        """Запустить все воркеры"""
        for _ in range(self.__count_workers):
            start_worker(self.__q_in, self.__q_out)

    def stop(self):
        """Остановить все воркеры"""
        for _ in range(self.__count_workers):
            self.__q_in.put((0, None))

    def append(self, luna: LunaCode, bot_state: dict):
        """Добавить в очередь задачу"""
        # очередь с приоритетами
        self.__q_in.put((luna.priority, (luna, bot_state)), block=True)

    def get_result(self) -> Tuple[List, Dict]:
        """Получить из очереди результат"""
        try:
            return self.__q_out.get(block=True)  # , timeout=timeout + 0.05)
        except QueueEmpty:
            # todo как-то пробрасывать код ошибки выше
            return [], {}


def start_worker(q_in: PriorityQueue, q_out: Queue):
    """Запустить один воркер"""
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
        except BaseException:  # pylint: disable=broad-except
            log.exception('')
            # todo как-то пробрасывать код ошибки выше
        watchdog.cancel()
        q_out.put((table2list(result), table2dict(internal_state)))

    log.info('%s shutdown', process_name)
