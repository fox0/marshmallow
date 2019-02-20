import logging

from core.luna import LunaCode
from core.worker import Workers, TaskWorker

__version__ = '0.4.2'

log = logging.getLogger('marshmallow')

TASK_TIMEOUT = 60.0


def run_pattern(luna: LunaCode, bot_state, *args):
    luna.execute()
    result, internal_state = luna.globals.main(bot_state, *args)
    return list(result), dict(internal_state)


def main():
    workers = Workers()
    workers.start()

    patterns = load_patterns()

    log.debug('running patterns…')

    lll = []

    bot_state = {'a': 0}

    for _ in range(5):
        for luna in patterns:
            t = TaskWorker(run_pattern, (luna, bot_state, 500_000), timeout=TASK_TIMEOUT)
            workers.add_task(t)
    for _ in range(5):
        for _ in range(len(patterns)):
            lll.append(workers.get_result(timeout=TASK_TIMEOUT))

    print(lll)

    workers.stop()


def load_patterns():
    log.debug('load_patterns')
    result = []
    luna = LunaCode('init')
    luna.execute()
    if not luna.globals.requirements_pattern:
        log.error('in init.lua not found "requirements_pattern"')
        return result
    for name in luna.globals.requirements_pattern.values():
        assert isinstance(name, str)
        try:
            result.append(LunaCode(name))
        except FileNotFoundError as e:
            log.error(e)
    return result


if __name__ == '__main__':
    from multiprocessing import freeze_support

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    freeze_support()  # ?
    main()
