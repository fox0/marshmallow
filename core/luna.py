import os
import logging

from lupa import LuaRuntime

log = logging.getLogger(__name__)

DIR_PATTERNS = 'patterns'
DEFAULT_TIMEOUT = 0.5


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

    __slots__ = ('name', 'lua_code', 'globals', 'timeout', 'input_fields', 'output_fields')

    def __init__(self, name: str, lua_code: str = None, is_clean_globals: bool = True):
        """

        :param name: имя паттерна
        :param lua_code: код скрипта. Если не указано, то будет считан из файла.
        """
        self.name = name
        if lua_code:
            self.lua_code = lua_code
        else:
            filename = os.path.join(DIR_PATTERNS, name + '.lua')
            with open(filename) as f:
                self.lua_code = f.read()

        # ещё один забавный хак: выполняем скрипт один раз, чтобы прочитать глобальные переменные
        self.execute()
        self.timeout = float(self.globals.timeout or DEFAULT_TIMEOUT)
        self.input_fields = table2list(self.globals.input_fields)
        self.output_fields = table2list(self.globals.output_fields)

        # и быстро затираем сложный объект, делая вид, что его не было
        if is_clean_globals:
            self.globals = None

    def execute(self):
        """Отложенная инициализация self.globals"""
        # потому что объект LuaRuntime нельзя передать между процессами
        # lua._state cannot be converted to a Python object for pickling
        lua = LuaRuntime(unpack_returned_tuples=False)
        self.globals = lua.globals()

        # хак, после которого внезапно начинает работать require()
        self.globals.package.path = os.path.join(DIR_PATTERNS, '?.lua') + ';' + self.globals.package.path

        lua.execute(self.lua_code)

    def __repr__(self):
        return "<LunaCode '%s' timeout=%s>" % (self.name, self.timeout)

    def __eq__(self, other):
        for i in ('name', 'lua_code', 'timeout', 'input_fields', 'output_fields'):
            if getattr(self, i) != getattr(other, i):
                return False
        return True

#
# def get_lunacode(name: str) -> LunaCode:
#     return LunaCode()
