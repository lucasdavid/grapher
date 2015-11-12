import abc

from . import base


class CacheRepository(base.Repository, metaclass=abc.ABCMeta):
    pass


class CacheEntityRepository(CacheRepository, base.EntityRepository):
    def find(self, identities):
        pass

    def all(self, skip=0, limit=None):
        pass

    def where(self, skip=0, limit=None, **query):
        pass

    def create(self, entities):
        pass

    def update(self, entities):
        pass

    def delete(self, identities):
        pass
