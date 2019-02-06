import logging
from lupa import LuaRuntime

__version__ = '0.4.0'

log = logging.getLogger(__name__)


def main():
    with open('patterns/test.lua') as f:
        lua_code = f.read()
    lua = LuaRuntime(unpack_returned_tuples=False)
    lua.execute(lua_code)
    g = lua.globals()
    print(g.run(55))


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s',
        level=logging.DEBUG
    )
    main()
