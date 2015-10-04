from unittest import TestCase
from nose_parameterized import parameterized

from grapher.resources import Resource


class ResourceTest(TestCase):
    @parameterized.expand([
        ('test', '/test'),
        ('/test', '/test'),
        ('Custom-Test', '/custom-test'),
        (None, '/resource')
    ])
    def test_real_end_point(self, end_point, expected):
        Resource.end_point = end_point

        actual = Resource.real_end_point()
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ('test', 'test'),
        ('Test', 'Test'),
        (None, 'Resource'),
    ])
    def test_real_name(self, name, expected):
        Resource.name = name

        actual = Resource.real_name()
        self.assertEqual(actual, expected)

    @parameterized.expand([
        (None, 200, True, {}, {}),
        ([], 200, True, {}, {'content': []}),
        ([1, 2, 3], 200, True, {}, {'content': [1, 2, 3]}),
        ([1, 2, 3], 200, False, {}, [1, 2, 3]),
        ([1, 2, 3], 200, True, {'count': 3}, {'content': [1, 2, 3], 'count': 3}),
        ({'test': 1}, 200, False, {}, {'test': 1}),
        ({'test': 1}, 404, True, {}, {'content': {'test': 1}}),
    ])
    def test_response(self, content, status_code, wrap, meta, expected):
        actual_response, actual_status = Resource.response(content, status_code, wrap, **meta)

        self.assertEqual(actual_status, status_code)

        if isinstance(expected, dict):
            self.assertDictEqual(actual_response, expected)

        elif isinstance(expected, list):
            self.assertListEqual(actual_response, expected)

        else:
            self.assertEqual(actual_response, expected)

    def test_response_raises_error_when_not_wrapping_lists(self):
        with self.assertRaises(ValueError):
            Resource.response([1, 2, 3], count=3, wrap=False)

    def test_options(self):
        class User(Resource):
            name = 'test-user'
            end_point = 'awesome-test-user'
            methods = ('GET', 'POST')

        expected = {'description': 'Resource test-user', 'methods': ('GET', 'POST'), 'uri': '/awesome-test-user'}

        actual = User().options()
        self.assertDictEqual(actual, expected)
