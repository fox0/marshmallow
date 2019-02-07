import os
import time
import signal
import logging
import threading

log = logging.getLogger(__name__)


class WatchDog(object):
    __slots__ = ('time', 'is_running')

    def __init__(self, timeout=0.2):
        log.debug('watchdog starting…')
        self.time = 0
        self.is_running = False
        threading.Thread(target=thread_watchdog, args=(self, timeout)).start()

    def start(self):
        """Вызывать в начале обработки задания"""
        self.time = time.time()
        self.is_running = True

    def stop(self):
        """Вызывать после обработки задания"""
        self.is_running = False

    def _get_delta(self):
        if not self.is_running:
            return 0
        return time.time() - self.time


def thread_watchdog(watchdog: WatchDog, timeout: float):
    while True:
        time.sleep(timeout)
        # if is_stop:  # todo stop
        #     break
        # noinspection PyProtectedMember
        if watchdog._get_delta() > timeout:
            log.error('process was kill by timeout > %s', timeout)
            os.kill(os.getpid(), signal.SIGKILL)  # NOTE: грязно, но другие способы не работают
            # todo run_process
    # log.debug('watchdog stop')
