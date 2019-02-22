import pickle
import unittest

from core.luna import LunaCode, table2list, table2dict


class TestLuaCheckInstall(unittest.TestCase):
    """Тестируем что lua и luaJIT нормально установились"""

    def setUp(self):
        from lupa import LuaRuntime
        self.lua = LuaRuntime()

    def test_lua_version(self):
        r = self.lua.eval('_VERSION')
        print(r)
        self.assertEqual(r, 'Lua 5.1')

    def test_luajit(self):
        self.assertEqual(self.lua.eval('jit == nil'), False)

    def test_luajit2(self):
        r = self.lua.eval('jit.version')
        print(r)  # LuaJIT 2.1.0-beta3
        self.assertIn('LuaJIT', r)


class TestLunaCodeFile(unittest.TestCase):
    def setUp(self):
        with open('test.lua') as f:
            lua_code = f.read()
        self.luna = LunaCode('test_filename', lua_code)

    def test_pickle(self):
        b = pickle.dumps(self.luna)
        luna2 = pickle.loads(b)
        self.assertEqual(self.luna, luna2)

    def test_global_vars(self):
        self.assertEqual(self.luna.timeout, 0.2)

    def test_global_vars2(self):
        self.assertEqual(self.luna.input_fields, ['var'])

    def test_global_vars3(self):
        self.assertEqual(self.luna.output_fields, ['a'])

    def test_global_execute(self):
        self.luna.execute()
        result, internal_state = self.luna.globals.main({'var': 11})
        result = table2list(result)
        internal_state = table2dict(internal_state)
        self.assertEqual(result, [42])
        self.assertEqual(internal_state, {})

    def test_global_execute2(self):
        self.luna.execute()
        result, internal_state = self.luna.globals.main({'var': 1})
        result = table2list(result)
        internal_state = table2dict(internal_state)
        self.assertEqual(result, [42])
        self.assertEqual(internal_state, {'a': 1})
