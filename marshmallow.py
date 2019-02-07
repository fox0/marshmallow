import logging
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count

from core.pattern import Pattern, read_pattern
from core.watchdog import WatchDog

__version__ = '0.4.0'

log = logging.getLogger('marshmallow')

TASK_TIMEOUT = 9999999


def process_worker(q_in: Queue, q_out: Queue):
    watchdog = WatchDog(timeout=TASK_TIMEOUT)
    for func, args in iter(q_in.get, None):
        watchdog.start()
        result = None
        try:
            log.debug('%s run %s%s', current_process().name, func.__name__, args)
            result = func(*args)
        except BaseException:
            log.exception('error:')
        q_out.put(result)
        watchdog.stop()


def main():
    q_in, q_out = Queue(), Queue()
    number_cpu = cpu_count()
    log.debug('running %d process…', number_cpu)
    for i in range(number_cpu):
        Process(target=process_worker, args=(q_in, q_out)).start()

    ls = ('test', 'test', 'test', 'test', 'test',)
    ls2 = [(name, read_pattern(name)) for name in ls]

    log.debug('running patterns…')
    for _ in range(3):
        for name, lua_code in ls2:
            q_in.put((task_run, (name, lua_code, 5000000)))
        for _ in range(len(ls)):  # todo lock
            print(q_out.get())

    log.debug('shutdown…')
    number_cpu = cpu_count()  # todo
    for i in range(number_cpu):
        q_in.put(None)


def task_run(name, lua_code, *args):
    p = Pattern(name, lua_code)
    return p.globals.main(*args)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    freeze_support()  # ?
    main()
