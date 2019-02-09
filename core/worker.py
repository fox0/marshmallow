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
    log.debug('%s ready', current_process().name)

    def kill_self():
        start_worker(q_in, q_out)
        log.error('worker will kill by timeout')
        os.kill(os.getpid(), signal.SIGKILL)

    for timeout, func, args in iter(q_in.get, None):
        watchdog = threading.Timer(timeout, kill_self)
        watchdog.start()
        result = None
        try:
            log.debug('%s %s%s', current_process().name, func.__name__, args)
            result = func(*args)
        except BaseException:
            log.exception('error:')
        q_out.put(result)
        watchdog.cancel()

    log.debug('%s shutdown', current_process().name)
