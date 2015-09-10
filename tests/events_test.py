from unittest import TestCase
from nose_parameterized import parameterized
from grapher.events import EventManager


class EventManagerTest(TestCase):

    @parameterized.expand([
        ('before_retrieve', lambda e: e),
        ('during_create', lambda e: e),
        ('after_delete', lambda e: e),
        ('on_startup', lambda e: e),
    ])
    def test_register(self, event, handler):
        m = EventManager()

        m.register(event, handler)

        self.assertIn(event, m.events)
        self.assertIn(handler, m.events[event])

    @parameterized.expand([
        ('', lambda e:e),
        ('before_create', None),
        ('', None),
        (None, None),
    ])
    def test_register_raises_on_invalid_event_or_handler(self, event, handler):
        m = EventManager()

        with self.assertRaises(ValueError):
            m.register(event, handler)
