import abc
from py2neo import Graph, Node, batch

from . import common, errors
from .. import settings


class Repository(metaclass=abc.ABCMeta):
    def __init__(self, resource_name, schema):
        self.resource_name = resource_name
        self.schema = schema
        self.identity = common.SchemaNavigator.identity_field_from(schema)

    def all(self, skip=0, limit=None):
        raise NotImplementedError

    def find(self, identity):
        raise NotImplementedError

    def where(self, **query):
        raise NotImplementedError

    def create(self, entities):
        raise NotImplementedError

    def update(self, entities):
        raise NotImplementedError

    def delete(self, entities):
        raise NotImplementedError


class GraphRepository(Repository):
    _g = None

    @property
    def g(self):
        self._g = self._g or Graph('http://%s:%s@%s' % (
            settings.ProductionSettings.DATABASES['default']['username'],
            settings.ProductionSettings.DATABASES['default']['password'],
            settings.ProductionSettings.DATABASES['default']['uri'],
        ))

        return self._g

    def _data_from_nodes(self, nodes):
        """Retrieve nodes' attributes.

        Serializer is expecting a list of dictionaries, but GraphRepository will always return a list of nodes.
        To fix this, let's transform these nodes into dictionaries.

        :param nodes: the list of nodes to be projected.
        :return: a list of dictionaries that represent the nodes's attributes.
        """
        entries = []

        nodes, transformed = common.CollectionHelper.transform(nodes)

        for node in nodes:
            entry = node.properties
            entry[self.identity] = node._id

            entries.append(entry)

        return common.CollectionHelper.restore(entries, transformed)

    def _nodes_from_data(self, d):
        """Retrieve nodes from data contained in plain dictionaries.

        :param d: the list of dictionaries.
        :return: a list of nodes created from the data contained in :d.
        """
        nodes = []

        d, transformed = common.CollectionHelper.transform(d)

        for entry in d:
            if self.identity in entry:
                # The entry claims to have an identity! Let's bind the node to a database node.
                node = self.g.node(entry[self.identity])
                # Delete entry's identity so it won't be shown as a property.
                del entry[self.identity]

                for field, value in entry.items():
                    node[field] = value
            else:
                # That's a new entry. Just creates a new node.
                node = Node(self.resource_name, **entry)

            nodes.append(node)

        return common.CollectionHelper.restore(nodes, transformed)

    def all(self, skip=0, limit=None):
        nodes = self.g.find(self.resource_name, limit=limit)
        return self._data_from_nodes(nodes)

    def find(self, identity):
        node = self.g.find_one(
            self.resource_name,
            self.identity,
            identity)
        return self._data_from_nodes(node)

    def where(self, **query):
        if len(query) != 1:
            raise errors.GrapherError('GraphRepository.where does not support multiple parameter filtering yet.')

        nodes = self.g.find(self.resource_name, *query.popitem())

        return self._data_from_nodes(nodes)

    def create(self, entities):
        entities = self._nodes_from_data(entities)
        entities = self.g.create(*entities)

        return self._data_from_nodes(entities)

    def update(self, entities):
        entities = self._nodes_from_data(entities)

        self.g.push(*entities)
        return self._data_from_nodes(entities)

    def delete(self, entities):
        entities = self._nodes_from_data(entities)
        entities = self.g.delete(*entities)

        return self._data_from_nodes(entities)
