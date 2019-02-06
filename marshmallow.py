import os.path
import logging
from multiprocessing import Process, Queue, current_process, freeze_support, cpu_count

from lupa import LuaRuntime, LuaError

__version__ = '0.4.0'

log = logging.getLogger('marshmallow')

DEBUG = True


def worker(q_in, q_out):
    for func, args in iter(q_in.get, None):
        try:
            log.debug('%s run %s%s', current_process().name, func.__name__, args)
            # tmp = threading.Thread(target=do_work, args=(id, lambda: stop_threads))
            result = func(*args)  # todo timeout
            q_out.put(result)
        except BaseException:
            log.exception('error:')
            q_out.put(None)


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


def main():
    number_cpu = cpu_count()
    log.debug('running %d process…', number_cpu)
    q_in, q_out = Queue(), Queue()
    for i in range(number_cpu):
        Process(target=worker, args=(q_in, q_out)).start()

    log.debug('load patterns…')
    patterns = ('test', 'test', 'test', 'test', 'test',)
    for i in patterns:
        q_in.put((task_read_pattern, (i,)))  # todo delme
    codes = []
    for _ in range(len(patterns)):
        r = q_out.get()
        if r is not None:
            codes.append(r)

    log.debug('running…')
    for i in codes:
        q_in.put((task_task, (i,)))

    for _ in range(len(codes)):
        print(q_out.get())

    log.debug('shutdown…')
    for i in range(number_cpu):
        q_in.put(None)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG if DEBUG else logging.INFO)
    freeze_support()  # ?
    main()
