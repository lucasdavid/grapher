import abc
from .. import commons


class Repository(metaclass=abc.ABCMeta):
    """Repository base interface.

    Extended by :EntityRepository and :RelationshipRepository.
    """

    connection_string = None

    def __init__(self, label, schema):
        """Construct a repository of a :label, constrained by a :schema.

        :param label: :str: which represents the entity in the persistence back-end.
        :param schema: :dict: which constrains entities :label of this repository.
        """
        self.label = label
        self.schema = schema
        self.identity = commons.SchemaNavigator.identity_from(schema)

    def from_dict_of_dicts(self, entries):
        return [e for i, e in entries.items()], list(entries.keys())

    def to_dict_of_dicts(self, entities, indices=None):
        if indices is None:
            indices = range(len(entities))

        indices = iter(indices)
        return {next(indices): e for e in entities}

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

    def create(self, entities, raise_errors=False):
        """Create and return the created entities.

        The dict of :entities has dictionaries' instances, each containing
        data related to a new entity to be created in the database.

        This method must return a pair containing dict of dictionaries that
        represent the instances created (or failed) in the same order they
        were passed in :entities.

        :param entities: :dict of dictionaries that represent the data to be
            created, indexed by the order in which they appeared in the request.
        :param raise_errors: flag if errors should be raised or silenced.

        :return :pair of dicts: (created, failed) containing the entities
            created and failed indexed by their original order.
        """
        raise NotImplementedError

    def update(self, entities, raise_errors=False):
        """Update and return the entities.

        The dict of :entities contains dictionaries that represent the data to
        be updated in their respective entity. Each dictionary has, necessarily,
        the key contained in :self.identity, and can be accessed as such:
        data[self.identity].

        This method must return a pair containing dict of dictionaries that
        represent the instances updated (or failed) in the same order they were
        passed in :entities.

        :param raise_errors: flag if errors should be raised or silenced.
        :param entities: :dict of dictionaries that represent the data to be
        updated, indexed by the order in which they appeared in the request.

        :return :pair of dicts: (updated, failed) containing the entities
        updated and failed indexed by their original order.
        """
        raise NotImplementedError

    def delete(self, entities, raise_errors=False):
        """Delete entities and return them.

        The dict of :entities to be deleted, instances of
        :self.schema[self.identity]['type'].

        This method must return a pair containing dict of dictionaries that
        represent the instances deleted (or failed) in the same order they
        were passed in :entities.

        :param entities: :dict of dictionaries that represent the data to be
        deleted, indexed by the order in which they appeared in the request.
        :param raise_errors: flag if errors should be raised or silenced.

        :return :pair of dicts: (deleted, failed) containing the entities
        deleted and failed indexed by their original order.
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
        """Match all relationships, as long as they share the same label with
        this repository.

        The list retrieved is based on the :origin and :target entities and
        the :self.label property of this repository.
        This method must return a list of dictionaries that represent the
        relationship. On each dictionary, the keys '_origin' and '_target'
        must be present.

        :param origin: the identity of the entity which is the origin of
            the relationship.
        :param target: the identity of the entity which is the target of
            the relationship.
        :param skip: the number of elements to skip when retrieving.
            If None, none element should be skipped.
        :param limit: the maximum length of the list retrieved.
            If None, returns all elements after :skip.
        """
        raise NotImplementedError
