import abc
from pymongo import MongoClient, UpdateOne

from . import base
from .. import settings


class MongodbRepository(metaclass=abc.ABCMeta):
    connection_string = settings.effective.DATABASES['mongodb']
    _database = None
    _mongodb_client = None

    @property
    def mongodb_client(self):
        self._mongodb_client = self._mongodb_client or \
                               MongoClient(**{k: self.connection_string[k] for k in {'host', 'port'}})
        return self._mongodb_client

    @property
    def database(self):
        self._database = self._database or self.mongodb_client[self.connection_string['name']]
        return self._database

    def _merge_entities_and_ids(self, entities, ids):
        ids = iter(ids)

        for entity in entities:
            entity.update({self.identity: next(ids)})

        return entities

    def _result(self, entities):
        entities = list(entities)

        for e in entities:
            e[self.identity] = str(e[self.identity])

        return entities


class MongodbEntityRepository(MongodbRepository, base.EntityRepository):
    def all(self, skip=0, limit=None):
        limit = 0 if limit is None else limit
        return self._result(self.database[self.label].find(skip=skip, limit=limit))

    def find(self, identities):
        return self._result(self.database[self.label].find({'_id': {'$in': identities}}))

    def where(self, skip=0, limit=None, **query):
        limit = 0 if limit is None else limit
        return self._result(self.database[self.label].find(query, skip=skip, limit=limit))

    def create(self, entities):
        ids = self.database[self.label].insert_many(entities).inserted_ids

        return self._result(
            self._merge_entities_and_ids(entities, ids))

    def update(self, entities):
        return self.database[self.label].bulk_write(
            (UpdateOne({'_id': e[self.identity]}, {'$set': e}) for e in entities), ordered=True)

    def delete(self, identities):
        return self.database[self.label].delete_many({'_id': {'$in': identities}})


class MongodbRelationshipRepository(MongodbRepository, base.RelationshipRepository):
    def all(self, skip=0, limit=None):
        pass

    def find(self, identities):
        pass

    def where(self, skip=0, limit=None, **query):
        pass

    def create(self, entities):
        pass

    def update(self, entities):
        pass

    def delete(self, identities):
        pass

    def match(self, origin=None, target=None, skip=0, limit=None):
        pass
