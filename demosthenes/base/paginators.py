from flask import request

from .common import It


class Paginator(object):
    def __init__(self, data, skip=None, limit=None):
        self.url = request.url
        self.base_url = request.base_url

        self.skip = skip or request.args.get('skip')
        if isinstance(self.skip, str):
            self.skip = int(self.skip)
        self.limit = limit or request.args.get('limit')
        if isinstance(self.limit, str):
            self.limit = int(self.limit)

        self._data = data

    def paginate(self):
        self.skip = self.skip or 0
        self.limit = self.limit or len(self._data)

        self._data = It.make_iterable(self._data)
        total = len(self._data)

        data = self._data[self.skip:self.skip + self.limit]
        count = len(data)

        previous_page = self.base_url + '?skip=%s&limit=%s' % (
            max(0, self.skip - self.limit), self.limit) if self.skip else None
        next_page = self.base_url + '?skip=%s&limit=%s' % (
            self.skip + count, self.limit) if self.skip + count < total else None

        return {
            '_metadata': {
                'url': self.url,
                'skip': self.skip,
                'limit': self.limit,
                'count': count,
                'total': total,
            },
            '_navigation': {
                'previous': previous_page,
                'next': next_page
            },
            'data': data
        }
