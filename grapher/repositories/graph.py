import abc
import py2neo
from py2neo import Graph, Node, Relationship

from . import base
from .. import errors, settings


class GraphRepository(base.Repository, metaclass=abc.ABCMeta):
    _g = None
    connection_string = settings.effective.DATABASES['neo4j']

    @property
    def g(self):
        self._g = self._g or Graph('http://%s:%s@%s' % (
            self.connection_string['username'],
            self.connection_string['password'],
            self.connection_string['uri'],
        ))

        return self._g

    def _build(self, identities):
        """Build entities or relationships based on their identities.

        :param identities: :list of identities compatible with
        self.schema[self.identity]['type'].

        :return: a list of :nodes or :relationships corresponding to
        the identities passed, in order.
        """
        raise NotImplementedError

    def find(self, identities):
        entities = self._build(identities)

        try:
            self.g.pull(*entities)
        except py2neo.GraphError:
            raise errors.NotFoundError(('NOT_FOUND', identities))

        return self.to_dict_of_dicts(entities)

    def create(self, entities, raise_errors=False):
        entities = self.from_dict_of_dicts(entities)
        entities = self.g.create(*entities)

        return self.to_dict_of_dicts(entities), {}

    def update(self, entities, raise_errors=False):
        entities = self.from_dict_of_dicts(entities)

        self.g.push(*entities)

        return self.to_dict_of_dicts(entities), {}

    def delete(self, identities, raise_errors=False):
        entities = self._build(identities)
        entities = self.g.delete(*entities)

        return self.to_dict_of_dicts(entities), {}


class GraphEntityRepository(GraphRepository, base.EntityRepository):
    def _build(self, identities):
        return [self.g.node(i) for i in identities]

    def from_dict_of_dicts(self, entries):
        nodes = []

        for i, entry in entries.items():
            # Find if the node exists on the database or is a new node.
            if self.identity in entry:
                # The entry claims to have an identity,
                # bind the node to a database node.
                node = self.g.node(entry[self.identity])
                del entry[self.identity]
            else:
                # That's a new entry. Create a new node.
                node = Node(self.label)

            node.properties.update(entry)
            nodes.append(node)

        return nodes

    def to_dict_of_dicts(self, entities, indices=None):
        entries, entities = [], list(entities)

        for node in entities:
            e = node.properties
            e[self.identity] = node._id

            entries.append(e)

        return super().to_dict_of_dicts(entries)

    def all(self, skip=0, limit=None):
        if limit is not None:
            limit += skip

        nodes = self.g.find(self.label, limit=limit)

        # Discard :skip elements.
        for _ in range(skip):
            next(nodes)

        return self.to_dict_of_dicts(nodes)

    def where(self, skip=0, limit=None, **query):
        if len(query) != 1:
            raise ValueError('GraphRepository.where does not support '
                             'multiple parameter filtering yet.')

        # TODO: Allow multiple keys when searching. This issue might help:
        # http://stackoverflow.com/questions/27795874/py2neo-graph-find-one-with-multiple-key-values
        query_item = query.popitem()
        if query_item[0] == self.identity:
            return self.find((query_item[1],))

        if limit is not None:
            limit += skip

        nodes = self.g.find(self.label, *query_item, limit=limit)

        for _ in range(skip):
            next(nodes)

        return self.to_dict_of_dicts(nodes)


class GraphRelationshipRepository(GraphRepository, base.RelationshipRepository):
    def _build(self, identities):
        return [self.g.relationship(i) for i in identities]

    def from_dict_of_dicts(self, entries):
        entities, indices = super().from_dict_of_dicts(entries)

        relationships = []

        for r in entities:
            if self.identity in r:
                relationship = self.g.relationship(r)
            else:
                origin = self.g.node(r['_origin'])
                target = self.g.node(r['_target'])

                relationship = Relationship(origin, self.label.upper(), target)

            # Delete meta properties, if present.
            if self.identity in r:
                del r[self.identity]
            if '_origin' in r:
                del r['_origin']
            if '_target' in r:
                del r['_target']

            relationship.properties.update(r)
            relationships.append(relationship)

        return relationships, indices

    def to_dict_of_dicts(self, entities, indices=None):
        relationships = []

        for r in entities:
            e = r.properties
            e[self.identity] = r._id
            e['_origin'] = r.start_node._id
            e['_target'] = r.end_node._id

            relationships.append(e)

        return super().to_dict_of_dicts(relationships, indices)

    def all(self, skip=0, limit=None):
        """Match all relationships, as long as they share the same label
        with this repository.

        :param skip: the number of elements to skip when retrieving.
        If None, none element should be skipped.

        :param limit: the maximum length of the list retrieved.
        If None, returns all elements after :skip.
        """
        return self.match(skip=skip, limit=limit)

    def match(self, origin=None, target=None, skip=0, limit=None):
        if origin:
            origin = self.g.node(origin)
        if target:
            target = self.g.node(target)
        if limit is not None:
            limit += skip

        relationships = self.g.match(origin, self.label.upper(), target,
                                     limit=limit)

        for _ in range(skip):
            next(relationships)

        return self.to_dict_of_dicts(relationships)

    def where(self, skip=0, limit=None, **query):
        if len(query) != 1:
            raise ValueError('GraphRepository.where does not support'
                             'multiple parameter filtering yet.')

        query_item = query.popitem()
        if query_item[0] == self.identity:
            return self.find((query_item[1],))

        raise NotImplementedError
