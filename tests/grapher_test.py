from unittest import TestCase
from grapher import Grapher, settings

settings.effective = settings.Testing


class GrapherTest(TestCase):
    def test_load_modules_raise_error(self):
        settings.Testing.BASE_MODULE = None
        expected_name = 'testgraphermodule'

        with self.assertRaises(ValueError):
            Grapher(expected_name)

    def test_load_modules(self):
        settings.Testing.BASE_MODULE = 'tests.examples'
        expected_name = 'testgraphermodule'

        g= Grapher(expected_name)

        self.assertIs(g.settings, settings.effective)
        self.assertEqual(g.app.name, expected_name)
        self.assertGreater(len(g.api.endpoints), 0)
