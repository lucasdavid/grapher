import abc
from .. import commons


class Manager(metaclass=abc.ABCMeta):
    def __init__(self, schema):
        self.schema = schema

    @property
    def repository(self):
        return self.schema.repository

    def identify(self, entities):
        identified, unidentified = {}, {}

        for i, entity in entities.items():
            if self.schema.Meta.identity in entity:
                identified[i] = entity
            else:
                unidentified[i] = entity

        return identified, unidentified

    def all(self, skip=0, limit=None):
        return self.repository.all(skip=skip, limit=limit)

    def find(self, identities):
        return self.repository.find(identities)

    def fetch(self, entities):
        entities, unidentified = self.identify(entities)
        return self.find(
                (e[self.schema.Meta.identity] for i, e in entities.items())), unidentified

    def query(self, query, skip=0, limit=None):
        return self.repository.where(skip=skip, limit=limit, **query)

    def query_or_all(self, query, skip=0, limit=None):
        return self.query(query, skip, limit) if query else self.all(skip,
                                                                     limit)

    def create(self, entities):
        return self.repository.create(entities)

    def update(self, entities):
        return self.repository.update(entities)

    def delete(self, entities):
        return self.repository.delete(entities)


class EntityManager(Manager):
    pass


class RelationshipManager(Manager):
    pass
