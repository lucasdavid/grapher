from unittest import TestCase
from unittest.mock import Mock
from nose_parameterized import parameterized
from grapher.resources import Resource, SchematicResource, EntityResource


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
        ([1, 2, 3], 200, True, {'count': 3}, {'content': [1, 2, 3], '_meta': {'count': 3}}),
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


class SchematicResourceTest(TestCase):
    def test_init(self):
        r = SchematicResource()

        self.assertIn('_id', r.schema)
        self.assertIn('identity', r.schema['_id'])
        self.assertTrue(r.schema['_id']['identity'])

        SchematicResource.schema = {'name': {'type': 'integer', 'identity': True}}
        r = SchematicResource()

        self.assertIn('name', r.schema)
        self.assertIn('identity', r.schema['name'])
        self.assertTrue(r.schema['name']['identity'])


class ModelResourceTest(TestCase):
    def test_get(self):
        r = EntityResource()
        r._repository = Mock()
        r._repository.all = Mock(return_value=[{'test': 1} for _ in range(4)])
        r._serializer = Mock()
        r._serializer.project = Mock(side_effect=lambda d: (d, ['test']))
        r._paginator = Mock()
        r._paginator.paginate = Mock(side_effect=lambda d: (d, {}))

        response, status = r.get()

        self.assertEqual(status, 200)
        self.assertIn('_meta', response)
        self.assertIn('page', response['_meta'])
        self.assertIn('projection', response['_meta'])

        self.assertIn('content', response)
        self.assertEqual(len(response['content']), 4)
