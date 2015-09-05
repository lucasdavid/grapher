from unittest import TestCase
from nose_parameterized import parameterized

from grapher import validators


class GraphValidatorTest(TestCase):
    @parameterized.expand([
        ({'_id': {'type': 'integer', 'identity': True}}, {'_id': 1}, True),
        ({'_id': {'type': 'string', 'identity': True}}, {'_id': 'test name'}, True),
        ({'_id': {'type': 'integer', 'identity': True}}, {}, True),
        ({'_id': {'type': 'integer'}}, {}, True),
        ({'_id': {'type': 'integer', 'identity': False}}, {}, True),
        ({'_id': {'type': 'integer', 'identity': False}}, {'_id': 1}, True),
        ({'age': {'type': 'integer', 'visible': False}}, {'age': 21}, True),
        ({'name': {'type': 'string', 'index': True}}, {'name': 'test'}, True),
    ])
    def test_valid_identities(self, schema, document, expected):
        v = validators.GrapherValidator(schema)
        actual = v.validate(document)

        self.assertEqual(actual, expected, (schema, document))
