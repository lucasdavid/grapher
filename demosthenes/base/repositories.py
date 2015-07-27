import abc
from py2neo import Graph

from . import Model, errors
from .. import settings


class Repository(object, metaclass=abc.ABCMeta):
    def __init__(self, model):
        if not issubclass(model, Model):
            raise errors.ComponentInstantiationError(self, model)

        self._model = model
        self._g = Graph(uri=settings.ProductionSettings.DATABASES['default']['url'])

    def all(self, limit=None):
        return self._g.find(self._model.__class__.__name__, limit=limit)

    def create(self, entity):
        raise NotImplementedError

    def update(self, entity):
        raise NotImplementedError

    def delete(self, ids):
        raise NotImplementedError
