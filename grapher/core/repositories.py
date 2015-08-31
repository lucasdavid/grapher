import abc
import py2neo
from py2neo import Graph, Node, Relationship

from . import commons, errors, settings


class Repository(metaclass=abc.ABCMeta):
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

    def link(self, links):
        raise NotImplementedError

    def find_link(self, origin=None, target=None, limit=None):
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
        if not nodes:
            return nodes

        entries = []
        nodes, transformed = commons.CollectionHelper.transform(nodes)

        for node in nodes:
            e = node.properties
            e[self.identity] = node._id

            entries.append(e)

        return commons.CollectionHelper.restore(entries, transformed)

    def _nodes_from_data(self, d):
        """Retrieve nodes from data contained in plain dictionaries.

        :param d: the list of dictionaries.
        :return: a list of nodes created from the data contained in :d.
        """
        if not d:
            return d

        nodes = []
        d, transformed = commons.CollectionHelper.transform(d)

        for e in d:
            # Find if the node exists on the database or is a new node.
            if self.identity in e:
                # The entry claims to have an identity, bind the node to a database node.
                node = self.g.node(e[self.identity])
                del e[self.identity]
            else:
                # That's a new entry. Create a new node.
                node = Node(self.label)

            node.properties.update(e)
            nodes.append(node)

        return nodes

    def _data_from_links(self, links):
        """Retrieve links' attributes.

        Serializer is expecting a list of dictionaries, but GraphRepository will always return a list of links.
        To fix this, let's transform these links into dictionaries.

        :param links: the list of links to be projected.
        :return: a list of dictionaries that represent the links's attributes.
        """
        if not links:
            return links

        entries = []
        links, transformed = commons.CollectionHelper.transform(links)

        for link in links:
            e = link.properties
            e[self.identity] = link._id
            e['_origin'] = link.start_node._id
            e['_target'] = link.end_node._id

            entries.append(e)

        return commons.CollectionHelper.restore(entries, transformed)

    def _links_from_data(self, d):
        if not d:
            return d

        links = []
        d, transformed = commons.CollectionHelper.transform(d)

        for e in d:
            if self.identity in e:
                link = self.g.relationship(e)
            else:
                origin = self.g.node(e['_origin'])
                target = self.g.node(e['_target'])

                link = Relationship(origin, self.label.upper(), target)

            # Delete meta properties, if present.
            if self.identity in e:
                del e[self.identity]
            if '_origin' in e:
                del e['_origin']
            if '_target' in e:
                del e['_target']

            link.properties.update(e)
            links.append(link)

        return links

    def all(self, skip=0, limit=None):
        if limit is not None:
            # Neo4J doesn't accept a :skip parameter, perhaps because the nodes
            # order might eventually change. If we've limited the number of entries returned,
            # we must add the number of entries skipped as well, so they can be removed by the serializer.
            limit += skip

        nodes = self.g.find(self.label, limit=limit)

        # Discard :skip elements.
        for _ in range(skip): next(nodes)

        return self._data_from_nodes(nodes)

    def find(self, identities):
        identities, _ = commons.CollectionHelper.transform(identities)
        nodes = [self.g.node(i) for i in identities]

        try:
            self.g.pull(*nodes)
        except py2neo.GraphError:
            raise errors.NotFoundError(
                ('NOT_FOUND', identities)
            )

        return self._data_from_nodes(nodes)

    def where(self, **query):
        if len(query) != 1:
            raise errors.GrapherError('GraphRepository.where does not support multiple parameter filtering yet.')

        nodes = self.g.find(self.label, *query.popitem())

        return self._data_from_nodes(nodes)

    def create(self, entities):
        nodes = self._nodes_from_data(entities)
        nodes = self.g.create(*nodes)

        return self._data_from_nodes(nodes)

    def link(self, links):
        links = self._links_from_data(links)
        links = self.g.create(*links)

        return self._data_from_links(links)

    def find_link(self, origin=None, target=None, limit=None):
        if origin:
            origin = self.g.node(origin)

        if target:
            target = self.g.node(target)

        links = self.g.match(origin, self.label.upper(), target, limit=limit)
        return self._data_from_links(links)

    def update(self, entities):
        nodes = self._nodes_from_data(entities)

        self.g.push(*nodes)

        return self._data_from_nodes(nodes)

    def delete(self, entities):
        entities = self._nodes_from_data(entities)
        entities = self.g.delete(*entities)

        return self._data_from_nodes(entities)
