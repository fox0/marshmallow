import os.path
import time
import logging
from collections import namedtuple
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count

from lupa import LuaRuntime, LuaError

__version__ = '0.4.0'

log = logging.getLogger('marshmallow')

DEBUG = True

MyTask = namedtuple('MyTask', ('func', 'args'))


def process_worker(q_in: Queue, q_out: Queue):
    for func, args in iter(q_in.get, None):  # MyTask
        # watch_dog.start()
        result = None
        try:
            log.debug('%s run %s%s', current_process().name, func.__name__, args)
            result = func(*args)
        except BaseException:
            log.exception('error:')
        q_out.put(result)
        # watch_dog.stop()


def run_workers(q_in, q_out):
    number_cpu = cpu_count()
    log.debug('running %d process…', number_cpu)
    for i in range(number_cpu):
        Process(target=process_worker, args=(q_in, q_out)).start()


def task_read_pattern(filename):
    fn = os.path.join('patterns', filename + '.lua')
    with open(fn) as f:
        return f.read()


def load_patterns(q_in, q_out):
    result = []
    log.debug('load patterns…')
    patterns = ('test', 'test', 'test', 'test', 'test',)
    for i in patterns:
        q_in.put(MyTask(task_read_pattern, (i,)))  # todo delme
    for _ in range(len(patterns)):
        r = q_out.get()
        if r is not None:
            result.append(r)
    assert len(result) > 0
    return result


def task_task(lua_code):
    lua = LuaRuntime(unpack_returned_tuples=False)
    try:
        lua.execute(lua_code)
    except LuaError as e:
        log.error(str(e).split('\n', 1)[0])
    g = lua.globals()
    return g.main(5000000)


def main():
    q_in, q_out = Queue(), Queue()
    run_workers(q_in, q_out)
    codes = load_patterns(q_in, q_out)

    log.debug('running patterns…')
    for i in codes:
        q_in.put(MyTask(task_task, (i,)))

    for _ in range(len(codes)):
        print(q_out.get())

    log.debug('shutdown…')
    number_cpu = cpu_count()  # todo
    for i in range(number_cpu):
        q_in.put(None)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG if DEBUG else logging.INFO)
    freeze_support()  # ?
    main()
