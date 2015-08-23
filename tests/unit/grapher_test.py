from unittest import TestCase
from grapher import Grapher


class GrapherTest(TestCase):
    def test_load_modules(self):
        result = Grapher().startup()

        self.assertTrue(result.resources)
