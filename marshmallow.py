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


def main():
    workers = Workers()
    workers.start()

    patterns = load_patterns()

    log.debug('running patterns…')
    for _ in range(3):
        for name, lua_code in patterns:
            workers.add_task(TaskWorker(run_pattern, (name, lua_code, 5_000_000), timeout=TASK_TIMEOUT))
        for _ in range(len(patterns)):
            print(workers.get_result(timeout=TASK_TIMEOUT))

    workers.stop()


if __name__ == '__main__':
    from multiprocessing import freeze_support

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    freeze_support()  # ?
    main()
