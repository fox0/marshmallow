import logging
from _queue import Empty

from core.luna import LunaCode
from core.pattern import load_patterns
from core.worker import Workers

__version__ = '0.4.1'

log = logging.getLogger('marshmallow')

TASK_TIMEOUT = 9999999


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
            workers.q_in.put((TASK_TIMEOUT, run_pattern, (name, lua_code, 5_000_000)))
        for _ in range(len(patterns)):
            try:
                print(workers.q_out.get(block=True, timeout=5))
            except Empty:
                print('timeout')

    workers.stop()


if __name__ == '__main__':
    from multiprocessing import freeze_support

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    freeze_support()  # ?
    main()
