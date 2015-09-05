from unittest import TestCase
from unittest.mock import Mock

from grapher.resources import EntityResource, RelationshipResource, SchematicResource, schematics
from grapher.parsers import query
from grapher import paginators, repositories


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


class EntityResourceTest(TestCase):
    def setUp(self):
        request = Mock()
        request.base_url = 'http://localhost/test'
        request.url = 'http://localhost/test?skip=2&limit=2'
        request.args = Mock()
        request.args.get = Mock(return_value=None)

        schematics.request = request
        query.request = request
        paginators.request = request

    def test_get(self):
        r = EntityResource()
        r._repository = Mock()
        r._repository.all = Mock(return_value=[{'test': 1} for _ in range(4)])
        r._serializer = Mock()
        r._serializer.project = Mock(side_effect=lambda d: (d, ['test']))
        r._paginator = Mock()
        r._paginator.paginate = Mock(side_effect=lambda d: (d, {}))

        response, status = r.get()

        self.assertEqual(status, 200, response)
        self.assertIn('_meta', response)
        self.assertIn('page', response['_meta'])
        self.assertIn('projection', response['_meta'])

        self.assertIn('content', response)
        self.assertEqual(len(response['content']), 4)


class RelationshipResourceTest(TestCase):
    def setUp(self):
        pass

    def test_init(self):
        class User(EntityResource):
            schema = {}

        class Group(EntityResource):
            schema = {}

        class Members(RelationshipResource):
            origin = Group
            target = User

        m = Members()

        self.assertIsNotNone(m)
        self.assertIn('_id', m.schema)
        self.assertIn('_id', m.origin.schema)
        self.assertIn('_id', m.target.schema)

    def test_init_fail_with_entity_repository(self):
        class User(EntityResource):
            schema = {}

        class Group(EntityResource):
            schema = {}

        class Members(RelationshipResource):
            origin = Group
            target = User
            repository_class = repositories.GraphEntityRepository

        with self.assertRaises(AssertionError):
            Members()

    def test_init_fail_with_invalid_origin_or_target(self):
        class User(EntityResource):
            schema = {}

        class Group(EntityResource):
            schema = {}

        class Members(RelationshipResource):
            pass

        with self.assertRaises(ValueError):
            Members()
        Members.origin = User

        with self.assertRaises(ValueError):
            Members()
        Members.origin = Members.target = Members

        with self.assertRaises(ValueError):
            Members()
        Members.origin = User
        with self.assertRaises(ValueError):
            Members()
        Members.target = Group

    def test_init_fails_with_invalid_cardinality(self):
        class User(EntityResource):
            schema = {}

        class Group(EntityResource):
            schema = {}

        class Members(RelationshipResource):
            origin = Group
            target = User
            cardinality = 'not-a-valid-cardinality'

        with self.assertRaises(ValueError):
            Members()

    def test_describe(self):
        class User(EntityResource):
            schema = {}

        class Group(EntityResource):
            schema = {}

        class Members(RelationshipResource):
            origin = Group
            target = User

        d = Members.describe()

        self.assertIn('relationship', d)
        self.assertIn('origin', d['relationship'])
        self.assertIn('target', d['relationship'])
        self.assertIn('cardinality', d['relationship'])
