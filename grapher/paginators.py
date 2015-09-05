import abc
from . import commons


class Paginator(metaclass=abc.ABCMeta):
    """Grapher's default paginator.

    Use this class to paginate :lists of data and construct metadata about this same pagination.
    """

    # If true, only collect metadata over the
    # passed data, without actually slicing it.
    soft_pagination = True

    @classmethod
    def paginate(cls, data, skip=None, limit=None):
        skip = skip or commons.request().args.get('skip') or 0
        skip = isinstance(skip, int) and skip or int(skip)

        limit = limit or commons.request().args.get('limit') or len(data)
        limit = isinstance(limit, int) and limit or int(limit)

        if not cls.soft_pagination:
            data = data[skip:limit]

        count = len(data)

        return data, {
            'current': commons.request().url,
            'previous': commons.request().base_url + '?skip=%s&limit=%s' % (
                max(0, skip - limit), limit) if skip else None,
            'next': commons.request().base_url + '?skip=%s&limit=%s' % (skip + count, limit),
            'skip': skip,
            'limit': limit,
            'count': count,
        }
