import abc
from py2neo import Graph, Node

from . import common
from .. import settings


class Repository(metaclass=abc.ABCMeta):
    def __init__(self, resource_name, schema):
        self.resource_name = resource_name
        self.schema = schema

    def all(self, skip=0, limit=None):
        raise NotImplementedError

    def find(self, identity):
        raise NotImplementedError

    def filter(self, query):
        raise NotImplementedError

    def create(self, entities):
        raise NotImplementedError

    def update(self, entities):
        raise NotImplementedError

    def delete(self, entities):
        raise NotImplementedError


class GraphRepository(Repository):
    _g = None

    def __init__(self, resource_name, schema):
        super().__init__(resource_name, schema)

        if '_meta' not in self.schema:
            self.schema['_meta'] = {}

        if 'identity' not in self.schema['_meta']:
            self.schema['_meta']['identity'] = '_id'

    @property
    def g(self):
        self._g = self._g or Graph('http://%s:%s@%s' % (
            settings.ProductionSettings.DATABASES['default']['username'],
            settings.ProductionSettings.DATABASES['default']['password'],
            settings.ProductionSettings.DATABASES['default']['uri'],
        ))

        return self._g

    def find(self, identity):
        return self.g.find_one(
            self.resource_name,
            self.schema['_meta']['identity'],
            identity)

    def all(self, skip=0, limit=None):
        return list(self.g.find(self.resource_name, limit=limit))

    def create(self, entities):
        entities = common.It.make_iterable(entities)
        return self.g.create([Node(self.resource_name, **e) for e in entities])

    def delete(self, entities):
        entities = common.It.make_iterable(entities)
        self.g.delete([Node(self.resource_name, **e) for e in entities])
