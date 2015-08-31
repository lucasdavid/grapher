import abc
import py2neo
from py2neo import Graph, Node, Relationship

from . import commons, errors, settings


class Repository(metaclass=abc.ABCMeta):
    """Repository base interface.

    Extended by :EntityRepository and :RelationshipRepository.
    """
    def __init__(self, label, schema):
        """Construct a repository of a :label, constrained by a :schema.

        :param label: :str: which represents the entity in the persistence back-end.
        :param schema: :dict: which constrains entities :label of this repository.
        """
        self.label = label
        self.schema = schema
        self.identity = commons.SchemaNavigator.identity_from(schema)

    def all(self, skip=None, limit=None):
        """Retrieve all elements that share :self.label.

        The return must be a list of dictionaries that represent the entities retrieved.

        :param skip: the number of elements to skip when retrieving. If None, none element should be skipped.
        :param limit: the maximum length of the list retrieved. If None, the list's length should is not limited.
        """
        raise NotImplementedError

    def find(self, identities):
        """Find :n entities that match the :n :identities.

        The return must be a list of dictionaries that represent the entities retrieved.
        This list is ordered in such way that the i-th element of the list is identified
        by the i-th identity in :identities.

        :param identities: the :n identities of the entities to be retrieved.
        """
        raise NotImplementedError

    def where(self, **query):
        """Retrieve a collection of entities that match the query.

        The return must be a list of dictionaries that represent the entities retrieved.
        The keys from the query must be joined by an AND operator.

        :todo: eventually, where should be modified to accept a object of :QuerySet,
        a more complete query representation.

        :param query: the query to be performed.
        """
        raise NotImplementedError

    def create(self, entities):
        """Create and return the created entities.

        The list :entities has dictionaries' instances, each containing
        data related to a new entity to be created in the database.
        This method must return a list containing dictionaries that represent
        the instances created in the same order they were passed in :entities.

        :param entities: :list of dictionaries that represent the data to be created.
        """
        raise NotImplementedError

    def update(self, entities):
        """Update and return the entities.

        The list :entities contains dictionaries that represent the data to be
        updated in their respective entity. Each dictionary has, necessarily, the key
        contained in :self.identity, and can be accessed as such: data[self.identity].
        This method must return a list containing dictionaries that represent
        the instances updated in the same order they were passed in :entities.

        :param entities: :list of dictionaries that represent the data to be updated.
        """
        raise NotImplementedError

    def delete(self, identities):
        """Delete and return the entities.

        The list :identities contains valid identities, instances of :self.schema[self.identity]['type'].
        This method must return a list containing dictionaries that represent
        the instances updated in the same order they were passed in :identities.

        :param identities: identities' :list that reference the entities to be deleted.
        """
        raise NotImplementedError


class EntityRepository(Repository, metaclass=abc.ABCMeta):
    """Repository for entities.

    Implementations of this interface will be used for entity-resources' persistence.
    """


class RelationshipRepository(Repository, metaclass=abc.ABCMeta):
    """Repository for entities.

    Implementations of this interface will be used for relationship-resources' persistence.
    """
    def find(self, origin=None, target=None, limit=None):
        """Find a list of relationships.

        The list retrieved is based on the :origin and :target entities and
        the :self.label property of this repository.
        This method must return a list of dictionaries that represent the relationship.
        On each dictionary, the keys '_origin' and '_target' must be present.

        :param origin: the identity of the entity which is the origin of the relationship.
        :param target: the identity of the entity which is the target of the relationship.
        :param limit: the maximum length of the list retrieved. If None, the list's length should is not limited.
        """
        raise NotImplementedError


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


class GraphEntityRepository(GraphRepository, EntityRepository):
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


class GraphRelationshipRepository(GraphRepository, RelationshipRepository):
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
