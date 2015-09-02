from unittest import TestCase
from unittest.mock import Mock
from grapher.docs import Docs


class DocsTest(TestCase):
    def setUp(self):
        self.expected = [
            Mock(), Mock()
        ]

        for i, resource in enumerate(self.expected):
            resource.real_name = Mock(return_value='test%i' % i)
            resource.real_end_point = Mock(return_value='/test%i' % i)
            resource.description = 'Description of resource test%i' % i
            resource.schema = {}
            resource.methods = ('GET', 'POST')

    def test_get(self):
        Docs.resources_to_describe = self.expected

        response, status_code = Docs().get()

        self.assertEqual(status_code, 200)

        self.assertIn('title', response)
        self.assertIn('description', response)
        self.assertIn('resources', response)

        self.assertEqual(len(response['resources']), len(self.expected))

        for i, resource in enumerate(self.expected):
            resource.real_name.assert_called_once()
            resource.real_end_point.assert_called_once()
