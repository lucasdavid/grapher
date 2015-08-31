import abc
import py2neo
from py2neo import Graph, Node, Relationship

from . import base
from .. import errors, settings


class GraphRepository(metaclass=abc.ABCMeta):
    _g = None

    @property
    def g(self):
        self._g = self._g or Graph('http://%s:%s@%s' % (
            settings.effective.DATABASES['default']['username'],
            settings.effective.DATABASES['default']['password'],
            settings.effective.DATABASES['default']['uri'],
        ))

        return self._g

    def _data_to_entities(self, d):
        """Transform entities from data.

        This method must return a :list of :entities ordered by the sequence
        that their correspondent have appeared in d.

        :param d: :list of :dict containing the data of the entities.
        :return: :list of :entities from :d.
        """
        raise NotImplementedError

    def _data_from_entities(self, entities):
        """Transform persisted entities to dictionaries.

        Serializer is expecting a list of dictionaries, but GraphRepository will always return a list of nodes.
        To fix this, transform these entities into dictionaries.

        :param entities: :list of entities that will be returned.
        :return: :list of :dict that represent the persisted entities.
        """
        raise NotImplementedError

    def create(self, entities):
        entities = self._data_to_entities(entities)
        entities = self.g.create(*entities)

        return self._data_from_entities(entities)

    def update(self, entities):
        entities = self._data_to_entities(entities)

        self.g.push(*entities)

        return self._data_from_entities(entities)

    def delete(self, entities):
        entities = self._data_to_entities(entities)
        entities = self.g.delete(*entities)

        return self._data_from_entities(entities)


class GraphEntityRepository(GraphRepository, base.EntityRepository):
    def _data_from_entities(self, entities):
        entries = []

        for node in entities:
            e = node.properties
            e[self.identity] = node._id

            entries.append(e)

        return entries

    def _data_to_entities(self, d):
        nodes = []

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

    def all(self, skip=None, limit=None):
        if not skip:
            skip = 0

        if limit is not None:
            # Neo4J doesn't accept a :skip parameter, perhaps because the nodes
            # order might eventually change. If we've limited the number of entries returned,
            # we must add the number of entries skipped as well, so they can be removed by the serializer.
            limit += skip

        nodes = self.g.find(self.label, limit=limit)

        # Discard :skip elements.
        for _ in range(skip):
            next(nodes)

        return self._data_from_entities(nodes)

    def find(self, identities):
        nodes = [self.g.node(i) for i in identities]

        try:
            self.g.pull(*nodes)
        except py2neo.GraphError:
            raise errors.NotFoundError(
                ('NOT_FOUND', identities)
            )

        return self._data_from_entities(nodes)

    def where(self, **query):
        if len(query) != 1:
            raise ValueError('GraphRepository.where does not support multiple parameter filtering yet.')

        nodes = self.g.find(self.label, *query.popitem())

        return self._data_from_entities(nodes)


class GraphRelationshipRepository(GraphRepository, base.RelationshipRepository):
    def _data_from_entities(self, entities):
        relationships = []

        for r in entities:
            e = r.properties
            e[self.identity] = r._id
            e['_origin'] = r.start_node._id
            e['_target'] = r.end_node._id

            relationships.append(e)

        return relationships

    def _data_to_entities(self, d):
        relationships = []

        for r in d:
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

        return relationships

    def find(self, origin=None, target=None, limit=None):
        if origin:
            origin = self.g.node(origin)

        if target:
            target = self.g.node(target)

        relationships = self.g.match(origin, self.label.upper(), target, limit=limit)
        return self._data_from_entities(relationships)
