import abc
import flask
from . import commons


class Paginator:
    """Grapher's default paginator.

    Use this class to paginate :lists of data and construct metadata about this same pagination.

    E.g.: when users request http://.../resource?skip=1&limit=1 and resource data is d = [1,2,3],

    Paginator().paginate(d)
    = [2], {
        'current':  'http://.../resource?skip=1&limit=1',
        'previous': 'http://.../resource?skip=0&limit=1',
        'next':     'http://.../resource?skip=2&limit=1',
        'skip': 1,
        'limit': 1,
        'count': 1,
        'total': 3,
    }

    """
    _request = None

    @property
    def request(self):
        self._request = self._request or flask.request
        return self._request

    def paginate(self, data, skip=None, limit=None):
        skip = skip or self.request.args.get('skip') or 0
        skip = isinstance(skip, int) and skip or int(skip)

        limit = limit or self.request.args.get('limit') or len(data)
        limit = isinstance(limit, int) and limit or int(limit)

        total = len(data)

        data = data[skip:skip + limit]
        count = len(data)

        return data, {
            'current': self.request.url,
            'previous': self.request.base_url + '?skip=%s&limit=%s' % (max(0, skip - limit), limit) if skip else None,
            'next': self.request.base_url + '?skip=%s&limit=%s' % (
                skip + count, limit) if skip + count < total else None,
            'skip': skip,
            'limit': limit,
            'count': count,
            'total': total,
        }
