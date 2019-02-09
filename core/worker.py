import os
import signal
import logging
import threading
from multiprocessing import Process, Queue, current_process, cpu_count

log = logging.getLogger(__name__)


class Workers(object):
    """
    example:
        def func():
            return 42

        workers = Workers()
        workers.start()
        timeout = 0.2
        workers.q_in.put((timeout, func, ()))
        print(workers.q_out.get())
        workers.stop()
    """

    __slots__ = ('q_in', 'q_out')

    def __init__(self):
        self.q_in = Queue()
        self.q_out = Queue()

    def start(self):
        for i in range(cpu_count()):
            start_worker(self.q_in, self.q_out)

    def stop(self):
        for i in range(cpu_count() * 2):  # на всякий случай
            self.q_in.put(None)


def start_worker(q_in: Queue, q_out: Queue):
    Process(target=process_worker, args=(q_in, q_out)).start()


def process_worker(q_in: Queue, q_out: Queue):
    process_name = current_process().name
    log.debug('%s ready', process_name)

    def kill_self():
        start_worker(q_in, q_out)
        log.error('worker will kill by timeout')
        os.kill(os.getpid(), signal.SIGKILL)

    for timeout, func, args in iter(q_in.get, None):
        log.debug('%s %s%s', process_name, func.__name__, args)
        watchdog = threading.Timer(timeout, kill_self)
        watchdog.start()
        result = None
        try:
            result = func(*args)
        except BaseException:
            log.exception('')
        watchdog.cancel()
        q_out.put(result)

    log.debug('%s shutdown', process_name)
