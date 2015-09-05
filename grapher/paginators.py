import abc
from flask_restful import request


class Paginator(metaclass=abc.ABCMeta):
    """Grapher's default paginator.

    Use this class to paginate :lists of data and construct metadata about this same pagination.
    """

    # If true, only collect metadata over the
    # passed data, without actually slicing it.
    soft_pagination = True

    @classmethod
    def paginate(cls, data, skip=None, limit=None):
        skip = skip or request.args.get('skip') or 0
        skip = isinstance(skip, int) and skip or int(skip)

        limit = limit or request.args.get('limit') or len(data)
        limit = isinstance(limit, int) and limit or int(limit)

        if not cls.soft_pagination:
            data = data[skip:skip + limit]

        count = len(data)

        return data, {
            'current': request.url,
            'previous': request.base_url + '?skip=%s&limit=%s' % (
                max(0, skip - limit), limit) if skip else None,
            'next': request.base_url + '?skip=%s&limit=%s' % (skip + count, limit),
            'skip': skip,
            'limit': limit,
            'count': count,
        }
