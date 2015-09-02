from unittest import TestCase

from cerberus import SchemaError
from grapher import commons


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
            actual = commons.SchemaNavigator.identity_from(schema)
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
            actual = commons.SchemaNavigator.identity_from(schema)
            self.assertEqual(expected, actual, schema)

    def test_schema_with_two_identities(self):
        schema = {
            'ssn': {'type': 'string', 'identity': True},
            '_id': {'type': 'integer', 'identity': True}
        }

        with self.assertRaises(SchemaError):
            commons.SchemaNavigator.identity_from(schema)


class CollectionHelper(TestCase):
    def setUp(self):
        self.collections = (
            (1, 2, 3),
            {1, 2, 3},
            [1, 2, 3],
        )

        self.items = (
            'Hello',
            1,
            {},
            dict(),
            lambda e: e,
        )

    def test_needs_collections(self):
        for c in self.collections:
            result = commons.CollectionHelper.needs(c)

            self.assertFalse(result, '%s should not need to be transformed.' % str(c))

    def test_needs_items(self):
        for i in self.items:
            result = commons.CollectionHelper.needs(i)

            self.assertTrue(result, '%s should need to be transformed.' % str(result))

    def test_transform_collections(self):
        for c in self.collections:
            result, transformed = commons.CollectionHelper.transform(c)

            self.assertIs(result, c)
            self.assertFalse(transformed, '%s->%s should not be transformed.' % (str(c), str(result)))

    def test_transform_items(self):
        for i in self.items:
            result, transformed = commons.CollectionHelper.transform(i)

            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIs(result[0], i)
            self.assertTrue(transformed, '%s should be transformed.' % str(i))

    def test_restore_transformed(self):
        for expected in self.items:
            actual = commons.CollectionHelper.restore([expected], previously_transformed=True)
            self.assertIs(actual, expected)

            actual = commons.CollectionHelper.restore(expected, previously_transformed=False)
            self.assertIs(actual, expected)

    def test_enumerate_collections(self):
        for c in self.collections:
            result, transformed = commons.CollectionHelper.enumerate(c)

            self.assertFalse(transformed, '%s should not be transformed.' % str(c))
            self.assertIsInstance(result, dict)
            self.assertEqual(len(result), len(c))

    def test_enumerate_items(self):
        for i in self.items:
            result, transformed = commons.CollectionHelper.enumerate(i)

            self.assertTrue(transformed, '%s should be transformed.' % str(i))
            self.assertIsInstance(result, dict)
            self.assertEqual(len(result), 1)
            self.assertIs(result[0], i)

    def test_restore_enumeration(self):
        e = {0: 1, 1: 2, 2: 3}

        result = commons.CollectionHelper.restore_enumeration(e, previously_transformed=False)
        self.assertListEqual(result, [1, 2, 3])

        e = {0: 1292}

        result = commons.CollectionHelper.restore_enumeration(e, previously_transformed=True)
        self.assertEqual(result, 1292)
