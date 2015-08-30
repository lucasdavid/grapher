from unittest import TestCase
from grapher.core import Grapher, settings


class GrapherTest(TestCase):
    def test_load_modules(self):
        expected_name = 'testgraphermodule'

        g = Grapher(expected_name)

        self.assertIs(g.settings, settings.effective)
        self.assertEqual(g.app.name, expected_name)
        self.assertGreater(len(g.api.endpoints), 0)
