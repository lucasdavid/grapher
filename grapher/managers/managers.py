from flask_restful import request
from grapher import parsers


class Manager:
    def __init__(self, name, schema, repository_class):
        self.name = name
        self.schema = schema
        self.repository_class = repository_class

    _repository = None

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.name, self.schema)
        return self._repository

    def all(self, skip=0, limit=None):
        return self.repository.all(skip=skip, limit=limit)

    def find(self, entities):
        return self.repository.find(entities)

    def query(self, query, skip=0, limit=None):
        return self.repository.where(skip=skip, limit=limit, **query)

    def query(self):
        skip = request.args.get('skip')
        skip = int(skip) if isinstance(skip, str) else 0

        limit = request.args.get('limit')
        limit = int(limit) if isinstance(limit, str) else None

        query = parsers.RequestQueryParser.query_as_object()

        return self.repository.where(skip=skip, limit=limit, **query) if query else self.all()

    def create(self, entities):
        return self.repository.create(entities)

    def update(self, entities):
        return self.update(entities)

    def delete(self, identities):
        return self.delete(identities)
