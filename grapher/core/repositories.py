import abc
import py2neo
from py2neo import Graph, Node, Relationship

from . import commons, errors
from .. import settings


class Repository(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, label, schema):
        self.label = label
        self.schema = schema
        self.identity = commons.SchemaNavigator.identity_from(schema)

    def all(self, skip=0, limit=None):
        raise NotImplementedError

    def find(self, identities):
        raise NotImplementedError

    def where(self, **query):
        raise NotImplementedError

    def create(self, entities):
        raise NotImplementedError

    def link(self, relationship, origin, target, properties=None):
        raise NotImplementedError

    def link_many(self, links):
        raise NotImplementedError

    def find_link(self, origin=None, target=None):
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
            settings.effective.DATABASES['default']['username'],
            settings.effective.DATABASES['default']['password'],
            settings.effective.DATABASES['default']['uri'],
        ))

        return self._g

    def _data_from_nodes(self, nodes):
        """Retrieve nodes' attributes.

        Serializer is expecting a list of dictionaries, but GraphRepository will always return a list of nodes.
        To fix this, let's transform these nodes into dictionaries.

        :param nodes: the list of nodes to be projected.
        :return: a list of dictionaries that represent the nodes's attributes.
        """
        if nodes is None:
            return None

        entries = []

        nodes, transformed = commons.CollectionHelper.transform(nodes)

        for node in nodes:
            entry = node.properties
            entry[self.identity] = node._id

            entries.append(entry)

        return commons.CollectionHelper.restore(entries, transformed)

    def _data_from_links(self, links):
        """Retrieve links' attributes.

        Serializer is expecting a list of dictionaries, but GraphRepository will always return a list of links.
        To fix this, let's transform these links into dictionaries.

        :param links: the list of links to be projected.
        :return: a list of dictionaries that represent the links's attributes.
        """
        if links is None:
            return None

        entries = []
        links, transformed = commons.CollectionHelper.transform(links)

        for link in links:
            entry = link.properties
            entry[self.identity] = link._id
            entry['_origin'] = link.start_node._id
            entry['_target'] = link.end_node._id

            entries.append(entry)

        return commons.CollectionHelper.restore(entries, transformed)

    def _nodes_from_data(self, d):
        """Retrieve nodes from data contained in plain dictionaries.

        :param d: the list of dictionaries.
        :return: a list of nodes created from the data contained in :d.
        """
        nodes = []
        d, transformed = commons.CollectionHelper.transform(d)

        for entry in d:
            # Find if the node exists on the database or is a new node.
            if self.identity in entry:
                # The entry claims to have an identity!
                # Let's bind the node to a database node.
                node = self.g.node(entry[self.identity])

                # Delete entry's identity so it won't be shown as a property.
                del entry[self.identity]
            else:
                # That's a new entry. Create a new node.
                node = Node(self.label)

            for field, value in entry.items():
                node[field] = value

            nodes.append(node)

        return nodes

    def _sync_relationships(self, nodes, d):
        creating, removing = [], []

        expected_relationships = {f for f in self.schema if 'relationship' in f}

        for i, node in enumerate(nodes):
            entry = d[i]

            for f in entry.keys() & expected_relationships:
                rel = f.upper()

                node_existing = set(node.match(rel))
                node_creating = {Relationship(node, rel, self.g.node(i)) for i in
                                 commons.CollectionHelper.transform(entry[f])}

                # Remove all that are not in creating.
                removing += list(node_existing - node_creating)
                # Remove all that were already created.
                creating += list(node_creating - node_existing)

        self.g.delete(*removing)
        self.g.create_unique(*creating)

    def all(self, skip=0, limit=None):
        nodes = self.g.find(self.label, limit=limit)
        return self._data_from_nodes(nodes)

    def find(self, identities):
        identities, _ = commons.CollectionHelper.transform(identities)
        nodes = [self.g.node(i) for i in identities]

        try:
            self.g.pull(*nodes)
        except py2neo.GraphError as e:
            raise errors.NotFoundError(
                ('NOT_FOUND', identities)
            )

        return self._data_from_nodes(nodes)

    def where(self, **query):
        if len(query) != 1:
            raise errors.GrapherError('GraphRepository.where does not support multiple parameter filtering yet.')

        nodes = self.g.find(self.label, *query.popitem())

        return self._data_from_nodes(nodes)

    def create(self, entities=[]):
        nodes = self._nodes_from_data(entities)
        nodes = self.g.create(*nodes)

        return self._data_from_nodes(nodes)

    def link(self, relationship, origin, target, properties=None):
        properties = properties or {}

        origin = self.g.node(origin)
        target = self.g.node(target)

        return Relationship(origin, relationship.upper(), target, **properties)

    def link_many(self, links):
        relationships = [self.link(*l) for l in links]
        return self.g.create(relationships)

    def find_link(self, origin=None, target=None):
        if origin:
            origin = self.g.node(origin)

        if target:
            target = self.g.node(target)

        links = self.g.match(origin, self.label.upper(), target)
        return self._data_from_links(links)

    def update(self, entities):
        nodes = self._nodes_from_data(entities)

        self.g.push(*nodes)

        return self._data_from_nodes(nodes)

    def delete(self, entities):
        entities = self._nodes_from_data(entities)
        entities = self.g.delete(*entities)

        return self._data_from_nodes(entities)
