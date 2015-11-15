from flask_restful import request
from .. import parsers, commons


class Manager:
    def __init__(self, name, schema, repository_class):
        self.name = name
        self.schema = schema
        self.repository_class = repository_class
        self.identity = commons.SchemaNavigator.identity_from(self.schema)

    _repository = None

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.name, self.schema)
        return self._repository

    def identify(self, entities):
        identified, unidentified = {}, {}

        for i, entity in entities.items():
            if self.identity in entity:
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
        return self.find((e[self.identity] for i, e in entities.items())), unidentified

    def query(self, query, skip=0, limit=None):
        return self.repository.where(skip=skip, limit=limit, **query)

    def query_or_all(self, query, skip=0, limit=None):
        return self.query(query, skip, limit) if query else self.all(skip, limit)

    def create(self, entities):
        return self.repository.create(entities)

    def update(self, entities):
        return self.update(entities)

    def delete(self, entities):
        return self.delete(entities)
