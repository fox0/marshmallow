import logging

from lupa import LuaRuntime, LuaError

log = logging.getLogger(__name__)

DIR_PATTERNS = 'patterns'


class LunaCode:
    """Враппер для выпонения lua-скритов"""

    __slots__ = ('name', 'lua_code', 'globals')

    def __init__(self, name: str):
        """

        :param name: имя паттерна
        """
        self.name = name
        with open('%s/%s.lua' % (DIR_PATTERNS, name)) as f:
            self.lua_code = f.read()
        self.globals = None

    def execute(self):
        """Отложенная инициализация"""
        # потому что объект LuaRuntime нельзя передать между процессами
        # self._state cannot be converted to a Python object for pickling
        lua = LuaRuntime(unpack_returned_tuples=False)
        self.globals = lua.globals()

        # хак, после которого внезапно начинает работать require()
        self.globals.package.path = '%s/?.lua;%s' % (DIR_PATTERNS, self.globals.package.path)

        try:
            lua.execute(self.lua_code)
        except LuaError as e:
            log.error('%s %s', self.name, str(e).split('\n', 1)[0])

    def __repr__(self):
        return "<LunaCode '%s'>" % self.name
