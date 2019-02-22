import logging

from lupa import LuaRuntime, LuaError

log = logging.getLogger(__name__)

DIR_PATTERNS = 'patterns'
DEFAULT_TIMEOUT = 0.5


def table2list(table) -> list:
    if not table:
        return []
    return list(table.values())


class LunaCode:
    """Враппер для выполнения lua-скритов"""

    __slots__ = ('name', 'lua_code', 'globals', 'timeout', 'input_fields', 'output_fields')

    def __init__(self, name: str, lua_code: str = None):
        """

        :param name: имя паттерна
        :param lua_code: код скрипта. Если не указано, то будет считан из файла.
        """
        self.name = name
        if lua_code:
            self.lua_code = lua_code
        else:
            with open('%s/%s.lua' % (DIR_PATTERNS, name)) as f:  # todo os.path.join
                self.lua_code = f.read()

        # ещё один забавный хак: выполняем скрипт один раз, чтобы прочитать глобальные переменные
        self.execute()
        self.timeout = float(self.globals.timeout or DEFAULT_TIMEOUT)
        self.input_fields = table2list(self.globals.input_fields)
        self.output_fields = table2list(self.globals.output_fields)
        # и быстро затираем сложный объект, делая вид, что его не было
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

    def __eq__(self, other):
        for i in ('name', 'lua_code', 'timeout', 'input_fields', 'output_fields'):
            if getattr(self, i) != getattr(other, i):
                return False
        return True
