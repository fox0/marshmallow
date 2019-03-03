#  Copyright (c) 2019. fox0 https://github.com/fox0/

# pylint: disable=missing-docstring, invalid-name
import logging

from core.luna import get_lunacode, table2list
from core.worker import Workers

__version__ = '0.5.1'

log = logging.getLogger('marshmallow')  # pylint: disable=invalid-name


def main():
    workers = Workers()
    workers.start()
    patterns = load_patterns()
    log.debug('running patterns…')

    bot_state = {
        'size': 500_000,
    }
    for _ in range(2):
        log.debug('bot_state: %s', bot_state)
        for _ in range(5):
            for luna in patterns:
                workers.append(luna, bot_state)

        acts, internal_state = [], []
        for _ in range(5):
            for _ in range(len(patterns)):
                a, s = workers.get_result()
                assert isinstance(a, list)
                assert isinstance(s, dict)
                acts.extend(a)
                internal_state.append(s)
        log.debug('acts: %s', acts)
        updated_fields = []
        for i in internal_state:
            for k, v in i.items():
                bot_state[k] = v
                if k in updated_fields:
                    log.warning("key '%s' in bot_state already was update", k)
                else:
                    updated_fields.append(k)

    workers.stop()


def load_patterns():
    log.debug('load_patterns')
    result = []
    luna = get_lunacode('init', is_clean_globals=False)  # todo а нужен ли он?!
    for name in table2list(luna.globals.requirements_pattern):
        try:
            result.append(get_lunacode(name))
        except FileNotFoundError as e:
            log.error(e)
    return result


if __name__ == '__main__':
    from multiprocessing import freeze_support

    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    freeze_support()  # ?
    main()
