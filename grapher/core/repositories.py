import abc
from py2neo import Graph, Node

from . import common, errors
from .. import settings


class Repository(metaclass=abc.ABCMeta):
    def __init__(self, resource_name, schema):
        self.resource_name = resource_name
        self.schema = schema

        # Let's assume :_id is the identity field.
        self.identity = '_id'

        # Now, we override :_id, if explicitly flagged by the user.
        for field, desc in self.schema.items():
            if 'identity' in desc and desc['identity']:
                self.identity = field

    def all(self, skip=0, limit=None):
        raise NotImplementedError

    def find(self, identity):
        raise NotImplementedError

    def where(self, **query):
        raise NotImplementedError

    def create(self, entities):
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
            settings.ProductionSettings.DATABASES['default']['username'],
            settings.ProductionSettings.DATABASES['default']['password'],
            settings.ProductionSettings.DATABASES['default']['uri'],
        ))

        return self._g

    def all(self, skip=0, limit=None):
        return list(self.g.find(self.resource_name, limit=limit))

    def find(self, identity):
        return self.g.find_one(
            self.resource_name,
            self.identity,
            identity)

    def where(self, **query):
        if len(query) != 1:
            raise errors.GrapherError('GraphRepository.where does not support multiple parameter filtering yet.')

        field, value = query.popitem()

        self.g.find(self.resource_name, field, value)

    def create(self, entities):
        return self.g.create(*[Node(self.resource_name, **e) for e in entities])

    def update(self, entities):
        entities = [Node(self.resource_name, **e) for e in entities]

        self.g.push(*entities)

        return entities

    def delete(self, entities):
        self.g.delete(*entities)

        return entities
