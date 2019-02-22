import logging

from lupa import LuaRuntime, LuaError

log = logging.getLogger(__name__)

DIR_PATTERNS = 'patterns'
DEFAULT_TIMEOUT = 0.5


class LunaCode:
    """Враппер для выполнения lua-скритов"""

    __slots__ = ('name', 'lua_code', 'globals', 'timeout', 'input_fields', 'output_fields')

    def __init__(self, name: str):
        """

        :param name: имя паттерна
        """
        self.name = name
        with open('%s/%s.lua' % (DIR_PATTERNS, name)) as f:
            self.lua_code = f.read()

        self.timeout = 10

        # todo не работает
        # ещё один забавный хак: выполняем скрипт один раз, чтобы прочитать глобальные переменные
        # self.execute()
        # self.timeout = self.globals.timeout or DEFAULT_TIMEOUT
        # self.input_fields = self.globals.input_fields or []
        # self.output_fields = self.globals.output_fields or []
        # и быстро затираем сложный объект, делая вид, что его не было
        # del self.globals
        self.globals = None

    def execute(self):
        """Отложенная инициализация self.globals"""
        # потому что объект LuaRuntime нельзя передать между процессами
        # lua._state cannot be converted to a Python object for pickling
        lua = LuaRuntime(unpack_returned_tuples=False)
        self.globals = lua.globals()

        # хак, после которого внезапно начинает работать require()
        self.globals.package.path = ';'.join((
            '%s/?.lua' % DIR_PATTERNS,  # todo os.path.join
            self.globals.package.path,
        ))
        try:
            lua.execute(self.lua_code)
        except LuaError as e:
            log.error('%s %s', self.name, str(e).split('\n', 1)[0])

    def __repr__(self):
        return "<LunaCode '%s' timeout=%s>" % (self.name, self.timeout)
