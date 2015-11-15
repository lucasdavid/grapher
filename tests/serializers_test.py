from unittest import TestCase
from unittest.mock import Mock
from nose_parameterized import parameterized
from grapher import serializers, errors


class SerializerTest(TestCase):
    @parameterized.expand([
        (
                {'a': {'type': 'string'}, 'b': {'type': 'integer'}},
                {0: {'a': 'a', 'b': 2}},
                {'a', 'b'}
        ),
        (
                {'a': {'type': 'string'}, 'b': {'type': 'integer', 'visible': False}},
                {0: {'a': 'a', 'b': 2}},
                {'a'}
        ),
        (
                {'a': {'type': 'string', 'visible': False}, 'b': {'type': 'integer', 'visible': False}},
                {0: {'a': 'a'}},
                set()
        ),
    ])
    def test_project(self, schema, data, expected_fields):
        s = serializers.Serializer('test', schema)
        result, fields = s.project(data)

        self.assertIsInstance(fields, list)

        fields = set(fields)
        self.assertEqual(fields, expected_fields)

        for i, entry in result.items():
            entry_fields = set(entry.keys())

            # No entry should have a field that isn't specified in fields.
            self.assertFalse(entry_fields - fields)

    @parameterized.expand([
        (
                {'a': {'type': 'string'}},
                {'a'}
        ),
        (
                {'a': {'type': 'string', 'visible': True}},
                {'a'}
        ),
        (
                {'a': {'type': 'string', 'visible': False}},
                set()
        ),
        (
                {'a': {'type': 'string', 'visible': False}, 'b': {'type': 'string', 'visible': True}},
                {'b'}
        ),
        (
                {'a': {'type': 'string', 'visible': True}, 'b': {'type': 'string', 'visible': True}},
                {'a', 'b'}
        ),
    ])
    def test_projected_fields(self, schema, expected):
        s = serializers.Serializer('test', schema)

        self.assertEqual(s.projected_fields, expected)

    @parameterized.expand([
        ({}, {0: {'a': 1}}, ({}, {0: {'a': 'unknown field'}}))
    ])
    def test_validate(self, schema, data, expected):
        s = serializers.Serializer('test', schema)
        accepted, declined = s.validate(data)

        self.assertDictEqual(accepted, expected[0])
        self.assertDictEqual(declined, expected[1])


class DynamicSerializerTest(TestCase):
    def setUp(self):
        r = Mock()
        r.args = Mock()
        r.args.get = Mock(return_value=None)

        serializers.request = r

    @parameterized.expand([
        ({'a': {'type': 'string'}, 'b': {'type': 'integer'}}, 'a', {'a'}),
        ({'a': {'type': 'string'}}, 'a', {'a'}),
        ({'a': {'type': 'string'}}, '', set()),
        ({'a': {'type': 'string'}, 'b': {'type': 'integer'}}, None, {'a', 'b'}),
    ])
    def test_projected_fields(self, schema, request_fields, expected):
        serializers.request.args.get.return_value = request_fields

        s = serializers.DynamicSerializer('test', schema)
        actual = s.projected_fields

        self.assertEqual(actual, expected)

    def test_projected_fields_store_result(self):
        s = serializers.DynamicSerializer('test', {'name': {'type': 'string'}})
        fields = s.projected_fields
        fields_a_second_time = s.projected_fields

        self.assertIs(fields, fields_a_second_time)

    def test_projected_fields_raises_bad_request(self):
        serializers.request.args.get.return_value = 'name,age,_id,products,test,test2'

        with self.assertRaises(errors.BadRequestError):
            serializers.DynamicSerializer('test', {}).projected_fields
