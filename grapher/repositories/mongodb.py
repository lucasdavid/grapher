import abc
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from . import base
from .. import settings


class MongodbRepository(base.Repository, metaclass=abc.ABCMeta):
    connection_string = settings.effective.DATABASES['mongodb']
    _database = None
    _mongodb_client = None

    @property
    def mongodb_client(self):
        self._mongodb_client = self._mongodb_client or \
                               MongoClient(
                                       **{k: self.connection_string[k] for k in
                                          {'host', 'port'}})
        return self._mongodb_client

    @property
    def database(self):
        self._database = self._database or self.mongodb_client[
            self.connection_string['name']]
        return self._database

    @property
    def collection(self):
        return self.database[self.label]

    def to_dict_of_dicts(self, entities, indices=None):
        entities = list(entities)

        for e in entities:
            e[self.schema.Meta.identity] = str(e[self.schema.Meta.identity])

        return super().to_dict_of_dicts(entities, indices)


class MongodbEntityRepository(MongodbRepository, base.EntityRepository):
    def all(self, skip=0, limit=None):
        limit = limit or 0

        entities = self.collection.find(skip=skip, limit=limit)
        return self.to_dict_of_dicts(entities)

    def find(self, identities):
        entities = self.collection.find({'_id': {'$in': identities}})
        return self.to_dict_of_dicts(entities)

    def where(self, skip=0, limit=None, **query):
        limit = limit or 0

        entities = self.collection.find(query, skip=skip, limit=limit)
        return self.to_dict_of_dicts(entities)

    def create(self, entities, raise_errors=False):
        entities, indices = self.from_dict_of_dicts(entities)

        result = self.collection.insert_many(entities)
        ids = iter(result.inserted_ids)

        for entity in entities:
            entity.update({self.schema.Meta.identity: str(next(ids))})

        return self.to_dict_of_dicts(entities, indices), {}

    def update(self, entities, raise_errors=False):
        entities, indices = self.from_dict_of_dicts(entities)
        failed = {}

        try:
            result = self.collection.bulk_write(
                    (UpdateOne({'_id': e[self.schema.Meta.identity]}, {'$set': e}) for e in
                     entities), ordered=True)

        except BulkWriteError as bulk_error:
            if raise_errors:
                raise

            for error in bulk_error['writeErrors']:
                i = error['index']

                indices.pop(i)
                entities.pop(i)

                failed[i] = error['errmsg']

        return self.to_dict_of_dicts(entities, indices), failed

    def delete(self, entities, raise_errors=False):
        entities, indices = self.from_dict_of_dicts(entities)

        result = self.collection.delete_many({'_id': {'$in': entities}})

        if result.deleted_count == len(entities):
            return self.to_dict_of_dicts(entities, indices), {}
        else:
            if raise_errors:
                raise BulkWriteError(result)

            return (self.to_dict_of_dicts(entities[:result.deleted_count],
                                          indices[:result.deleted_count]),
                    self.to_dict_of_dicts(entities[result.deleted_count:],
                                          indices[result.deleted_count:]))


class MongodbRelationshipRepository(MongodbRepository,
                                    base.RelationshipRepository):
    pass
