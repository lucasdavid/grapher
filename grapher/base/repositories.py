import abc
from py2neo import Graph

from .. import settings


class Repository(object, metaclass=abc.ABCMeta):
    def __init__(self, model):
        self._model = model

    def all(self, skip=0, limit=None):
        raise NotImplementedError

    def find(self, id):
        raise NotImplementedError

    def create(self, entity):
        raise NotImplementedError

    def update(self, entity):
        raise NotImplementedError

    def delete(self, ids):
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

    def find(self, id):
        return self.g.find_one(self._model['name'], 'id', id)

    def all(self, skip=0, limit=None):
        return list(self.g.find(self._model['name'], limit=limit))
