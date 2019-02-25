import pickle
import unittest

from lupa import LuaRuntime

from core.luna import LunaCode, table2list, table2dict


class TestLuaCheckInstall(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime()

    def test_luajit(self):
        self.assertFalse(self.lua.eval('jit == nil'))

    def test_luajit2(self):
        self.assertTrue(self.lua.eval('jit.status()')[0])


class TestLunaCodeFile(unittest.TestCase):
    def setUp(self):
        self.luna = LunaCode('', "require('test_luna')")

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


if __name__ == '__main__':
    unittest.main()
