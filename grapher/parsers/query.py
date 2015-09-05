import abc
import json
from flask_restful import request

from .. import errors


class RequestQueryParser(metaclass=abc.ABCMeta):
    request_query_keyword = 'query'
    operators = {'$and', '$or', '$not'}

    @classmethod
    def _is_operator(cls, key):
        return key[0] == '$'

    @classmethod
    def _validate_query(cls, query):
        if isinstance(query, dict):
            for key, value in query.items():
                if cls._is_operator(key) and key not in cls.operators:
                    raise errors.BadRequestError(
                        ('INVALID_QUERY', (key, str(query)), ('?where={$and:{"name": "grapher"}}',))
                    )

    @classmethod
    def query(cls):
        return request.args.get(cls.request_query_keyword) or ''

    @classmethod
    def query_as_object(cls):
        query = cls.query()
        if query:
            try:
                query = json.loads(query)
            except ValueError:
                raise errors.BadRequestError(('INVALID_QUERY', (str(query),)))

            cls._validate_query(query)

        return query or {}
