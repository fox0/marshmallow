import logging

from lupa import LuaRuntime, LuaError

log = logging.getLogger(__name__)


class LuaCode(object):
    __slots__ = ('name', 'globals')

    def __init__(self, name, lua_code):
        self.name = name
        lua = LuaRuntime(unpack_returned_tuples=False)
        try:
            lua.execute(lua_code)
        except LuaError as e:
            log.error('%s %s', name, str(e).split('\n', 1)[0])
        self.globals = lua.globals()