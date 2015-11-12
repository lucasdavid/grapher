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
        for key, value in query.items():
            if cls._is_operator(key) and key not in cls.operators:
                raise errors.BadRequestError(
                    ('INVALID_QUERY', (key, str(query)), ('?where={$and:{"name": "grapher"}}',))
                )

    @classmethod
    def query(cls):
        query = request.args.get(cls.request_query_keyword)

        if query:
            try:
                query = json.loads(query)
            except ValueError:
                raise errors.BadRequestError(('INVALID_QUERY', (str(query),)))

            cls._validate_query(query)

        return query or {}

    @classmethod
    def full_query(cls):
        query = parsers.RequestQueryParser.query_as_object()

        skip = request.args.get('skip')
        skip = int(skip) if isinstance(skip, str) else 0

        limit = request.args.get('limit')
        limit = int(limit) if isinstance(limit, str) else None

        return {'query': query, 'skip': skip, 'limit': limit}

    @classmethod
    def full_query_or_raise(cls):
        query = cls.full_query();

        if not query:
            raise errors.BadRequestError('MISSING_QUERY')

        return query
