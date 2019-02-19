import unittest


class Lua(unittest.TestCase):
    """Тестируем что lua и luaJIT нормально установились"""

    def setUp(self):
        from lupa import LuaRuntime
        self.lua = LuaRuntime()

    def test_lua_version(self):
        r = self.lua.eval('_VERSION')
        print(r)
        self.assertEqual(r, 'Lua 5.1')

    def test_luajit(self):
        r = self.lua.eval('jit.version')  # not nil
        print(r)
        self.assertIn('LuaJIT', r)
