from unittest import TestCase
from unittest.mock import Mock

import py2neo
from faker import Faker
from nose_parameterized import parameterized
from grapher import errors
from grapher.repositories.graph import GraphEntityRepository, GraphRelationshipRepository

f = Faker()


def fake_node(**properties):
    node = Mock()

    node._id = properties.get('id', f.random_int(min=0, max=100))
    node.properties = {
        'test1': properties.get('test1', f.random_int(min=0, max=100)),
        'test2': properties.get('test1', f.name()),
    }

    return node


def fake_relationship(link=None):
    rel = Mock()
    rel.properties = link.properties if link else {}
    rel._id = f.random_int(min=0, max=1000)
    rel.start_node = fake_node()
    rel.end_node = fake_node()

    return rel


class GraphEntityRepositoryTest(TestCase):
    def setUp(self):
        self.label = 'test'
        self.schema = {
            'test1': {'type': 'integer'},
            'test2': {'type': 'string'},
        }
        self.data = (fake_node() for _ in range(20))

        graph = Mock()
        graph.find = Mock(
            side_effect=lambda label, limit: (fake_node() for _ in range(limit is None and 4 or min(4, limit))))
        graph.node = Mock(side_effect=lambda i: fake_node())
        graph.pull = Mock()
        graph.push = Mock()
        graph.create = Mock(side_effect=lambda *e: (fake_node() for _ in range(len(e))))
        graph.delete = Mock(side_effect=lambda *e: e)

        self.r = GraphEntityRepository(self.label, self.schema)
        self.r._g = graph

    @parameterized.expand([
        (0, None, 4),
        (2, None, 2),
        (2, 2, 2),
        (0, 10, 4),
        (2, 10, 2),
    ])
    def test_all(self, skip, limit, expected_length):
        actual = self.r.all(skip, limit)

        self.r._g.find.assert_called_once_with(self.label, limit=limit and skip + limit or None)

        actual = list(actual)
        self.assertEqual(len(actual), expected_length)

    def test_find(self):
        identities = [1, 2, 3]
        actual = self.r.find(identities)

        self.assertEqual(self.r._g.node.call_count, len(identities))
        self.assertTrue(self.r._g.pull.called)
        self.assertEqual(len(actual), len(identities))

    def test_find_nonexistent_nodes(self):
        identities = [1, 2, 3]
        self.r._g.pull = Mock(side_effect=py2neo.GraphError)

        with self.assertRaises(errors.NotFoundError):
            self.r.find(identities)

    @parameterized.expand([
        (0, None, 4),
        (0, 2, 2),
        (2, 2, 2),
        (0, 10, 4),
        (2, 10, 2),
    ])
    def test_where(self, skip, limit, expected_length):
        self.r._g.find = Mock(
            side_effect=lambda p, q, r, limit=None: (fake_node() for _ in range(limit is None and 4 or min(limit, 4))))

        actual = self.r.where(test1=10, skip=skip, limit=limit)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), expected_length)

    def test_where_identity(self):
        actual = self.r.where(_id=10)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), 1)

    def test_where_raises_error_with_multiple_keys(self):
        with self.assertRaises(ValueError):
            self.r.where(test1=10, test2='test')

    def test_create(self):
        data = [fake_node().properties]

        actual = self.r.create(data)

        self.assertTrue(self.r._g.create.called)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), 1)

    def test_update(self):
        n = fake_node()
        data = [n.properties]
        data[0]['_id'] = n._id

        actual = self.r.update(data)

        self.assertTrue(self.r._g.push.called)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), 1)

    def test_delete(self):
        entities = [{'_id': d._id} for d in self.data]
        actual = self.r.delete(entities)

        self.assertTrue(self.r._g.delete.called)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), len(entities))


class GraphRelationshipRepositoryTest(TestCase):
    def setUp(self):
        self.schema = {'_id': {'type': 'integer'}, 'test': {'type': 'string'}}

        g = Mock()
        g.node = Mock(side_effect=lambda i: fake_node(id=i))
        g.relationship = Mock(side_effect=lambda i: fake_relationship())
        g.match = Mock(
            side_effect=lambda o, l, t, limit: (fake_relationship() for _ in range(limit and min(4, limit) or 4)))
        g.create = Mock(side_effect=lambda *r: r)

        self.g = g

    @parameterized.expand([
        (0, None, 4),
        (2, None, 2),
        (2, 2, 2),
    ])
    def test_all(self, skip, limit, expected_length):
        r = GraphRelationshipRepository('test', {})
        r._g = self.g

        actual = r.all(skip, limit)

        self.assertTrue(self.g.match.called)
        self.assertEqual(len(actual), expected_length)
        self.assertIsInstance(actual[0], dict)

    @parameterized.expand([
        (None, None),
        (1, None),
        (None, 2),
        (1, 2),
    ])
    def test_match(self, origin, target):
        r = GraphRelationshipRepository('test', {})
        r._g = self.g

        actual = r.match(origin, target)

        self.assertTrue(self.g.match.called)
        self.assertTrue('TEST', self.g.match.call_args[0][1])

        if origin is None:
            self.assertIsNone(self.g.match.call_args[0][0])
        else:
            self.assertIsNotNone(self.g.match.call_args[0][0])

        if target is None:
            self.assertIsNone(self.g.match.call_args[0][2])
        else:
            self.assertIsNotNone(self.g.match.call_args[0][2])
