import os.path
import logging
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count

from lupa import LuaRuntime, LuaError

from core.watchdog import WatchDog

__version__ = '0.4.0'

log = logging.getLogger('marshmallow')

DEBUG = True

TASK_TIMEOUT = 3.0


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

    codes = load_patterns(q_in, q_out)

    log.debug('running patterns…')
    for i in codes:
        q_in.put((task_task, (i,)))

    for _ in range(len(codes)):  # todo lock
        print(q_out.get())

    log.debug('shutdown…')
    # global is_stop
    # is_stop = True
    number_cpu = cpu_count()  # todo
    for i in range(number_cpu):
        q_in.put(None)


def load_patterns(q_in, q_out):
    result = []
    log.debug('load patterns…')
    patterns = ('test', 'test', 'test', 'test', 'test',)
    for i in patterns:
        q_in.put((task_read_pattern, (i,)))  # todo delme
    for _ in range(len(patterns)):
        r = q_out.get()
        if r is not None:
            result.append(r)
    assert len(result) > 0
    return result


def task_read_pattern(filename):
    fn = os.path.join('patterns', filename + '.lua')
    with open(fn) as f:
        return f.read()


def task_task(lua_code):
    lua = LuaRuntime(unpack_returned_tuples=False)
    try:
        lua.execute(lua_code)
    except LuaError as e:
        log.error(str(e).split('\n', 1)[0])
    g = lua.globals()
    return g.main(5000000)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG if DEBUG else logging.INFO)
    freeze_support()  # ?
    main()
