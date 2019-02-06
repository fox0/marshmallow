import os.path
import logging
import asyncio
from _asyncio import Task
from concurrent.futures import ALL_COMPLETED

from lupa import LuaRuntime, LuaError

__version__ = '0.4.0'

log = logging.getLogger('marshmallow')

DEBUG = True


async def read_pattern(filename):
    fn = os.path.join('patterns', filename + '.lua')
    with open(fn) as f:
        lua = LuaRuntime(unpack_returned_tuples=False)
        lua.execute(f.read())
        return lua


async def task(lua):
    g = lua.globals()
    g.main(5000000)


async def main():
    patterns = ('test', 'test', 'test', 'test', 'tes0t',)
    tasks = [read_pattern(i) for i in patterns]
    done, pending = await asyncio.wait(tasks, return_when=ALL_COMPLETED)
    assert len(done) == len(patterns)

    tasks = []
    for i in done:
        assert isinstance(i, Task)
        try:
            lua = i.result()
            tasks.append(task(lua))
        except FileNotFoundError as e:
            log.error(e)
        except LuaError as e:
            log.error(str(e).split('\n', 1)[0])
    done, pending = await asyncio.wait(tasks, timeout=1.0, return_when=ALL_COMPLETED)
    for i in done:
        assert isinstance(i, Task)
        i.result()

    if len(pending) > 0:
        log.debug('%d task(s) failed' % len(pending))
        for i in pending:
            assert isinstance(i, Task)
            i.cancel()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s %(funcName)s():%(lineno)d: %(message)s',
                        level=logging.DEBUG if DEBUG else logging.INFO)
    asyncio.run(main(), debug=DEBUG)
