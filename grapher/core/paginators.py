import abc
import flask
from . import commons


class Paginator(object):
    _request = None

    @property
    def request(self):
        self._request = self._request or flask.request
        return self._request

    def paginate(self, data, skip=None, limit=None):
        url = self.request.url
        base_url = self.request.base_url

        skip = skip or self.request.args.get('skip') or 0
        skip = isinstance(skip, int) and skip or int(skip)

        limit = limit or self.request.args.get('limit') or len(data)
        limit = isinstance(limit, int) and limit or int(limit)

        data, _ = commons.CollectionHelper.transform(data)
        total = len(data)

        content = data[skip:skip + limit]

        del data

        count = len(content)

        previous_page = base_url + '?skip=%s&limit=%s' % (
            max(0, skip - limit), limit) if skip else None
        next_page = base_url + '?skip=%s&limit=%s' % (
            skip + count, limit) if skip + count < total else None

        return content, {
            'current': url,
            'previous': previous_page,
            'next': next_page,
            'skip': skip,
            'limit': limit,
            'count': count,
            'total': total,
        }
