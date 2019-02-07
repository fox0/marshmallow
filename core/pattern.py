import os
import logging

from lupa import LuaRuntime, LuaError

log = logging.getLogger(__name__)

PATTERN_DIR = 'patterns'


class Pattern(object):
    __slots__ = ('name', 'globals')

    def __init__(self, name, lua_code):
        self.name = name
        lua = LuaRuntime(unpack_returned_tuples=False)
        try:
            lua.execute(lua_code)
        except LuaError as e:
            log.error(str(e).split('\n', 1)[0])
        self.globals = lua.globals()


def read_pattern(name):
    log.debug('load pattern %s…', name)
    with open(os.path.join(PATTERN_DIR, name + '.lua')) as f:
        return f.read()
