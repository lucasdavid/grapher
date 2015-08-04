from flask import request

from .common import It, DataCollector


class Paginator(DataCollector):
    def __init__(self):
        super().__init__()

    def paginate(self, skip=None, limit=None):
        url = request.url
        base_url = request.base_url

        skip = skip or request.args.get('skip') or 0
        skip = isinstance(skip, int) and skip or int(skip)

        limit = limit or request.args.get('limit') or len(self._data)
        limit = isinstance(limit, int) and limit or int(limit)

        self._data = It.make_iterable(self._data)
        total = len(self._data)

        content = self._data[skip:skip + limit]

        del self._data

        count = len(content)

        previous_page = base_url + '?skip=%s&limit=%s' % (
            max(0, skip - limit), limit) if skip else None
        next_page = base_url + '?skip=%s&limit=%s' % (
            skip + count, limit) if skip + count < total else None

        return {
            '_metadata': {
                'url': url,
                'skip': skip,
                'limit': limit,
                'count': count,
                'total': total,
            },
            '_navigation': {
                'previous': previous_page,
                'next': next_page
            },
            'content': content
        }
