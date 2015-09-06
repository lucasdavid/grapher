import abc
from .. import commons


class Repository(metaclass=abc.ABCMeta):
    """Repository base interface.

    Extended by :EntityRepository and :RelationshipRepository.
    """
    def __init__(self, label, schema, resource=None):
        """Construct a repository of a :label, constrained by a :schema.

        :param label: :str: which represents the entity in the persistence back-end.
        :param schema: :dict: which constrains entities :label of this repository.
        :param resource: instance of the resource associated with this repository.
        """
        self.label = label
        self.schema = schema
        self.identity = commons.SchemaNavigator.identity_from(schema)
        self.resource = resource

    def all(self, skip=0, limit=None):
        """Retrieve all elements that share :self.label.

        The return must be a list of dictionaries that represent the entities retrieved.

        :param skip: the number of elements to skip when retrieving. If None, none element should be skipped.
        :param limit: the maximum length of the list retrieved. If None, returns all elements after :skip.
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

    def where(self, skip=0, limit=None, **query):
        """Retrieve a collection of entities that match the query.

        The return must be a list of dictionaries that represent the entities retrieved.
        The keys from the query must be joined by an AND operator.

        :todo: eventually, where should be modified to accept a object of :QuerySet,
        a more complete query representation.

        :param skip: the number of elements to skip when retrieving. If None, none element should be skipped.
        :param limit: the maximum length of the list retrieved. If None, returns all elements after :skip.
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
    def match(self, origin=None, target=None, skip=0, limit=None):
        """Match all relationships, as long as they share the same label with this repository.

        The list retrieved is based on the :origin and :target entities and
        the :self.label property of this repository.
        This method must return a list of dictionaries that represent the relationship.
        On each dictionary, the keys '_origin' and '_target' must be present.

        :param origin: the identity of the entity which is the origin of the relationship.
        :param target: the identity of the entity which is the target of the relationship.
        :param skip: the number of elements to skip when retrieving. If None, none element should be skipped.
        :param limit: the maximum length of the list retrieved. If None, returns all elements after :skip.
        """
        raise NotImplementedError
