from unittest import TestCase
from nose_parameterized import parameterized

from grapher.core import serializers, errors


class SerializerTest(TestCase):
    @parameterized.expand([
        (
                {'a': {'type': 'string'}, 'b': {'type': 'integer'}},
                [{'a': 'a', 'b': 2}],
                {'a', 'b'}
        ),
        (
                {'a': {'type': 'string'}, 'b': {'type': 'integer', 'visible': False}},
                [{'a': 'a', 'b': 2}],
                {'a'}
        ),
        (
                {'a': {'type': 'string', 'visible': False}, 'b': {'type': 'integer', 'visible': False}},
                [{'a': 'a'}],
                set()
        ),
    ])
    def test_project(self, schema, data, expected_fields):
        s = serializers.Serializer(schema)
        result, fields = s.project(data)

        self.assertIsInstance(fields, list)

        fields = set(fields)
        self.assertEqual(fields, expected_fields)

        # Lists and dicts should keep being what they are.
        self.assertIs(type(result), type(data))

        if not isinstance(result, list):
            result = [result]

        for entry in result:
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
        s = serializers.Serializer(schema)

        self.assertEqual(s.projected_fields, expected)

    def test_validate_null_data(self):
        s = serializers.Serializer({})

        with self.assertRaises(errors.BadRequestError):
            s.validate(None)

    @parameterized.expand([
        ({}, [{'a': 1}], ([], {0: {'a': 'unknown field'}}))
    ])
    def test_validate(self, schema, data, expected):
        s = serializers.Serializer(schema)
        accepted, declined = s.validate(data)

        self.assertListEqual(accepted, expected[0])
        self.assertDictEqual(declined, expected[1])
