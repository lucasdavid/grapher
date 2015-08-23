from unittest import TestCase
from grapher.core.commons import SchemaNavigator


class SchemaNavigatorTest(TestCase):
    def test_schemas_without_identity(self):
        schemas = (
            {},
            {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
            },
            {
                'name': {'type': 'string', 'identity': False},
                'age': {'type': 'integer'},
            }
        )

        expected = '_id'

        for schema in schemas:
            actual = SchemaNavigator.identity_field_from(schema)
            self.assertEqual(expected, actual, schema)

    def test_schemas_with_identity(self):
        schemas = (
            {'_id': {'type': 'string', 'identity': True}},
            {'name': {'type': 'string', 'identity': True}},
            {'ssn': {'type': 'string', 'identity': True}},
            {'_id': {'type': 'integer', 'identity': True}},
        )

        expected_sequence = ('_id', 'name', 'ssn', '_id')

        for i, schema in enumerate(schemas):
            expected = expected_sequence[i]
            actual = SchemaNavigator.identity_field_from(schema)
            self.assertEqual(expected, actual, schema)
