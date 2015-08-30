from unittest import TestCase
from unittest.mock import Mock

from faker import Faker
from grapher.core import errors
from grapher.core.repositories import GraphRepository
import py2neo

f = Faker()


def fake_node():
    node = Mock()
    node.__id = f.random_int(min=0, max=1000)
    node.properties = {
        'test1': f.random_int(min=0, max=100),
        'test2': f.name(),
    }

    return node


class GraphRepositoryTest(TestCase):
    def setUp(self):
        self.label = 'test'
        self.schema = {
            'test1': {'type': 'integer'},
            'test2': {'type': 'string'},
        }
        self.data = (fake_node() for _ in range(20))

        graph = Mock()
        graph.find = Mock(side_effect=lambda label, limit: (fake_node() for _ in range(limit)))
        graph.node = Mock(side_effect=lambda i: fake_node())
        graph.pull = Mock()
        graph.push = Mock()
        graph.create = Mock(side_effect=lambda *e: (fake_node() for _ in range(len(e))))
        graph.delete = Mock(side_effect=lambda *e: e)

        self.r = GraphRepository(self.label, self.schema)
        self.r._g = graph

    def test_all(self):
        skip, limit = 2, 10

        actual = self.r.all(skip, limit)

        self.r._g.find.assert_called_once_with(self.label, limit=skip + limit)

        actual = list(actual)
        self.assertEqual(len(actual), limit)

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

    def test_where(self):
        self.r._g.find = Mock(side_effect=lambda p, q, r: (fake_node(),))

        actual = self.r.where(test1=10)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), 1)

    def test_where_with_multiple_keys(self):
        with self.assertRaises(errors.GrapherError):
            self.r.where(test1=10, test2='test')

    def test_create(self):
        data = fake_node().properties

        actual = self.r.create(data)

        self.assertTrue(self.r._g.create.called)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), 1)

    def test_delete(self):
        entities = [{'_id': d._id} for d in self.data]
        actual = self.r.delete(entities)

        self.assertTrue(self.r._g.delete.called)

        self.assertIsInstance(actual, list)
        self.assertEqual(len(actual), len(entities))

    def test_link(self):
        self.r._g.node = Mock(side_effect=lambda i: py2neo.Node(self.label))
        relationships = [('TESTS', 1, 2, {'test': 10})]

        result = self.r.link(relationships)

        self.assertIsNotNone(result)
