from unittest import TestCase
from unittest.mock import Mock
from faker import Faker

from grapher import serializers, paginators, repositories, settings
from grapher.resources import SchematicResource, schematics
from grapher.parsers import query
from tests.examples import resources as test_resources

settings.effective = settings.Testing

f = Faker()


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
        request.form = [{'name': f.name(), 'age': f.random_int(20, 40)} for _ in range(4)]

        schematics.request = request
        query.request = request
        paginators.request = request
        serializers.request = request

        self.data = [{'name': f.name(), 'age': f.random_int(20, 40)} for _ in range(4)]
        self.entities_with_ids = [{'_id': f.random_int(), 'name': f.name(), 'age': f.random_int(20, 40)} for _ in
                                  range(4)]

    def test_real_end_point(self):
        expected = 'testtest_test102312'

        class User(test_resources.User):
            end_point = expected

        expected = '/%s' % expected
        actual = User.real_end_point()

        self.assertEqual(actual, expected)

    def test_get(self):
        user = test_resources.User()
        user._repository = Mock()
        user._repository.all = Mock(return_value=[{'test': 1} for _ in range(4)])

        response, status = user.get()

        self.assertEqual(status, 200, response)
        self.assertIn('_meta', response)
        self.assertIn('page', response['_meta'])
        self.assertIn('projection', response['_meta'])

        self.assertIn('content', response)
        self.assertEqual(len(response['content']), 4)

    def test_get_with_request_params(self):
        schematics.request.args.get.side_effect = lambda key: key == 'skip' and '2' or key == 'limit' and '2' or None

        user = test_resources.User()
        user._repository = Mock()
        user._repository.all = Mock(return_value=self.data[2:4])

        response, status = user.get()

        self.assertEqual(status, 200, response)
        self.assertIn('_meta', response)
        self.assertIn('page', response['_meta'])
        self.assertIn('projection', response['_meta'])
        self.assertIn('content', response)
        self.assertEqual(len(response['content']), 2)

    def test_post(self):
        user = test_resources.User()
        user._repository = Mock()
        user._repository.create = Mock(side_effect=lambda e: e)

        response, status = user.post()

        self.assertEqual(status, 200)
        self.assertIn('_meta', response)
        self.assertIn('projection', response['_meta'])
        self.assertIn('created', response)
        self.assertEqual(len(response['created']), len(self.data))

    def test_put(self):
        schematics.request.form = self.entities_with_ids
        user = test_resources.User()
        user._repository = Mock()
        user._repository.find = Mock(side_effect=lambda e: self.entities_with_ids)
        user._repository.update = Mock(side_effect=lambda e: e)

        response, status = user.put()

        self.assertEqual(status, 200)
        self.assertIn('_meta', response)
        self.assertIn('projection', response['_meta'])
        self.assertIn('updated', response)
        self.assertEqual(len(response['updated']), len(self.data))

    def test_patch(self):
        schematics.request.form = self.entities_with_ids

        user = test_resources.User()
        user._repository = Mock()
        user._repository.find = Mock(side_effect=lambda e: self.entities_with_ids)
        user._repository.update = Mock(side_effect=lambda e: e)

        response, status = user.patch()

        self.assertEqual(status, 200)
        self.assertIn('_meta', response)
        self.assertIn('projection', response['_meta'])
        self.assertIn('updated', response)
        self.assertIn('failed', response)
        self.assertEqual(len(response['updated']), len(self.data))
        self.assertEqual(len(response['failed']), 0)

    def test_patch_empty_data(self):
        schematics.request.form = []

        user = test_resources.User()
        user._repository = Mock()
        user._repository.find = Mock(side_effect=lambda e: [])
        user._repository.update = Mock(side_effect=lambda e: e)

        response, status = user.patch()

        self.assertEqual(status, 400)
        self.assertIn('_meta', response)
        self.assertIn('errors', response['_meta'])
        self.assertIn('DATA_CANNOT_BE_EMPTY', response['_meta']['errors'])

    def test_patch_with_invalid_data(self):
        schematics.request.form = self.data

        user = test_resources.User()
        user._repository = Mock()
        user._repository.find = Mock(side_effect=lambda e: self.data)
        user._repository.update = Mock(side_effect=lambda e: e)

        response, status = user.patch()

        self.assertEqual(status, 400)
        self.assertIn('_meta', response)
        self.assertIn('errors', response['_meta'])
        self.assertIn('UNIDENTIFIABLE', response['_meta']['errors'])

    def test_delete_from_header(self):
        schematics.request.args.get.side_effect = lambda e: e == 'query' and '{"_id": -1}' or None
        user = test_resources.User()
        user._repository = Mock()
        user._repository.where = Mock(return_value=self.entities_with_ids)
        user._repository.delete = Mock(return_value=self.entities_with_ids)

        response, status = user.delete()

        self.assertEqual(status, 200)
        self.assertIn('_meta', response)
        self.assertIn('projection', response['_meta'])
        self.assertIn('deleted', response)
        self.assertEqual(len(response['deleted']), len(self.entities_with_ids))

    def test_delete_from_body(self):
        schematics.request.form = self.entities_with_ids
        user = test_resources.User()
        user._repository = Mock()
        user._repository.delete = Mock(side_effect=lambda e: self.entities_with_ids)

        response, status = user.delete()

        self.assertEqual(status, 200)
        self.assertIn('_meta', response)
        self.assertIn('projection', response['_meta'])
        self.assertIn('deleted', response)
        self.assertEqual(len(response['deleted']), len(self.entities_with_ids))

    def test_delete_empty_data(self):
        schematics.request.form = []

        user = test_resources.User()
        user._repository = Mock()

        response, status = user.delete()

        self.assertEqual(status, 400)
        self.assertIn('_meta', response)
        self.assertIn('errors', response['_meta'])
        self.assertIn('DATA_CANNOT_BE_EMPTY', response['_meta']['errors'])


class RelationshipResourceTest(TestCase):
    def setUp(self):
        pass

    def test_init(self):
        m = test_resources.Members()

        self.assertIsNotNone(m)
        self.assertIn('_id', m.schema)
        self.assertIn('_id', m.origin.schema)
        self.assertIn('_id', m.target.schema)

    def test_init_with_origin_and_target_as_strings(self):
        class Members(test_resources.Members):
            origin = 'Group'

        m = Members()

        self.assertIsNotNone(m)
        self.assertIn('_id', m.schema)
        self.assertIn('_id', m.origin.schema)
        self.assertIn('_id', m.target.schema)

        class Members(test_resources.Members):
            origin = test_resources.Group
            target = 'User'

        m = Members()

        self.assertIsNotNone(m)
        self.assertIn('_id', m.schema)
        self.assertIn('_id', m.origin.schema)
        self.assertIn('_id', m.target.schema)

    def test_init_fail_with_entity_repository(self):
        class Members(test_resources.Members):
            repository_class = repositories.GraphEntityRepository

        with self.assertRaises(AssertionError):
            Members()

    def test_init_fail_with_invalid_origin_or_target(self):
        class Members(test_resources.Members):
            origin = None
            target = None

        with self.assertRaises(ValueError):
            Members()
        Members.origin = test_resources.User

        with self.assertRaises(ValueError):
            Members()
        Members.origin = Members.target = Members

        with self.assertRaises(ValueError):
            Members()
        Members.origin = test_resources.User
        with self.assertRaises(ValueError):
            Members()
        Members.target = test_resources.Group

    def test_init_fails_with_invalid_cardinality(self):
        class Members(test_resources.Members):
            cardinality = 'not-a-valid-cardinality'

        with self.assertRaises(ValueError):
            Members()

    def test_describe(self):
        d = test_resources.Members.describe()

        self.assertIn('relationship', d)
        self.assertIn('origin', d['relationship'])
        self.assertIn('target', d['relationship'])
        self.assertIn('cardinality', d['relationship'])


class EntityResourceEventsTest(TestCase):
    def setUp(self):
        request = Mock()
        request.base_url = 'http://localhost/test'
        request.url = 'http://localhost/test'
        request.args = Mock()
        request.args.get = Mock(return_value=None)

        schematics.request = request
        query.request = request
        paginators.request = request
        serializers.request = request

    def test_after_retrieve(self):
        class User(test_resources.User):
            def after_retrieve(self, entries):
                for _ in range(2):
                    entries.pop()

        user = User()
        user._repository = Mock()
        user._repository.all = Mock(return_value=[{'test': 1} for _ in range(4)])

        response, status = user.get()

        self.assertEqual(status, 200, response)
        self.assertIn('_meta', response)
        self.assertIn('page', response['_meta'])
        self.assertIn('projection', response['_meta'])

        self.assertIn('content', response)
        self.assertEqual(len(response['content']), 2)
