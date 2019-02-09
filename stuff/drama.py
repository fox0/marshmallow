# apt-get install rabbitmq-server redis-server
# dramatiq[rabbitmq,redis,watch]
# dramatiq marshmallow --watch .

import logging

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.encoder import PickleEncoder
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

from core.lupa import LuaCode
from core.pattern import load_patterns

__version__ = '0.5.0a'

log = logging.getLogger('marshmallow')

broker = RabbitmqBroker()
broker.add_middleware(Results(backend=RedisBackend(encoder=PickleEncoder())))
dramatiq.set_broker(broker)


@dramatiq.actor(time_limit=0.3, max_retries=0, store_results=True)
def run_pattern(name, lua_code, *args):
    try:
        p = LuaCode(name, lua_code)
        return p.globals.main(*args)
    except dramatiq.middleware.time_limit.TimeLimitExceeded:
        return None


def main():
    patterns = load_patterns()
    log.debug('running patterns…')
    for _ in range(3):
        messages = []
        for name, lua_code in patterns:
            messages.append(run_pattern.send(name, lua_code, 5_000_000))
        for message in messages:
            try:
                print(message.get_result(block=True))
            except dramatiq.results.errors.ResultTimeout:
                print('timeout')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG)
    main()
