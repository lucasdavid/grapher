from unittest import TestCase
from unittest.mock import Mock

from grapher.core import paginators


class PaginatorTest(TestCase):
    def setUp(self):
        self.request = Mock()
        self.request.base_url = 'http://localhost/test'
        self.request.url = 'http://localhost/test?skip=2&limit=2'
        self.request.args = Mock()
        self.request.args.get = Mock(return_value=2)

    def test_paginate(self):
        data = [1, 2, 3, 4]

        p = paginators.Paginator()
        p._request = self.request

        content, page = p.paginate(data, 2, 2)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0], 3)
        self.assertEqual(content[1], 4)
