import logging

from core.luna import LunaCode
from core.pattern import load_patterns
from core.worker import Workers, TaskWorker

__version__ = '0.4.1'

log = logging.getLogger('marshmallow')

TASK_TIMEOUT = 60.0


def run_pattern(name, lua_code, *args):
    p = LunaCode(name, lua_code)
    return p.globals.main(*args)


def fff(size):
    import time
    import random
    st = time.time()
    a = [random.randint(1, size) for _ in range(size)]
    b = [random.randint(1, size) for _ in range(size)]

    def test():
        for i in range(size):
            if a[i] != b[i]:
                a[i] = a[i] + b[i]

    test()
    return time.time() - st


def main():
    workers = Workers()
    workers.start()

    patterns = load_patterns()

    log.debug('running patterns…')

    lll = []
    for name, lua_code in patterns:
        t = TaskWorker(run_pattern, (name, lua_code, 500_000), timeout=TASK_TIMEOUT)
        workers.add_task(t)
    for _ in range(len(patterns)):
        lll.append(workers.get_result(timeout=TASK_TIMEOUT))

    lll2 = []
    for _ in range(4):
        t = TaskWorker(fff, (500_000,), timeout=TASK_TIMEOUT)
        workers.add_task(t)
    for _ in range(4):
        lll2.append(workers.get_result(timeout=TASK_TIMEOUT))

    print(lll)
    print(lll2)

    workers.stop()


if __name__ == '__main__':
    from multiprocessing import freeze_support

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    freeze_support()  # ?
    main()
