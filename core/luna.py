import os
import logging

from lupa import LuaRuntime

log = logging.getLogger(__name__)

DIR_PATTERNS = 'patterns'
DEFAULT_TIMEOUT = 0.5
DEFAULT_PRIORITY = 0


def table2list(table) -> list:
    if not table:
        return []
    return list(table.values())


def table2dict(table) -> dict:
    if not table:
        return {}
    return dict(table)


class LunaCode:
    """Враппер для выполнения lua-скритов"""

    __slots__ = ('name', 'lua_code', 'globals', 'timeout', 'priority', 'input_fields', 'output_fields')

    def __init__(self, name: str, lua_code: str, is_clean_globals: bool = True):
        self.name = name
        self.lua_code = lua_code

        # ещё один забавный хак: выполняем скрипт один раз, чтобы прочитать глобальные переменные
        self.execute()
        self.timeout = float(self.globals.timeout or DEFAULT_TIMEOUT)
        self.priority = int(self.globals.priority or DEFAULT_PRIORITY)
        self.input_fields = table2list(self.globals.input_fields)
        self.output_fields = table2list(self.globals.output_fields)

        # и быстро затираем сложный объект, делая вид, что его не было
        if is_clean_globals:
            self.globals = None

    def execute(self):
        """Отложенная инициализация self.globals"""
        # потому что объект LuaRuntime нельзя передать между процессами
        # lua._state cannot be converted to a Python object for pickling

        # noinspection PyArgumentList
        lua = LuaRuntime(unpack_returned_tuples=False)
        self.globals = lua.globals()

        # хак, после которого внезапно начинает работать require()
        self.globals.package.path = os.path.join(DIR_PATTERNS, '?.lua') + ';' + self.globals.package.path

        lua.execute(self.lua_code)

    def __repr__(self):
        return "<LunaCode [%d] '%s' timeout=%s>" % (self.priority, self.name, self.timeout)

    def __eq__(self, other):
        # for tests
        for i in ('name', 'lua_code', 'timeout', 'priority', 'input_fields', 'output_fields'):
            if getattr(self, i) != getattr(other, i):
                return False
        return True


def get_lunacode(name: str, is_clean_globals=True) -> LunaCode:
    filename = os.path.join(DIR_PATTERNS, name + '.lua')
    with open(filename) as f:
        lua_code = f.read()
    return LunaCode(name, lua_code, is_clean_globals)
