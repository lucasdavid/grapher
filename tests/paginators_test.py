from unittest import TestCase
from unittest.mock import Mock, patch
from nose_parameterized import parameterized
from grapher import paginators


class PaginatorTest(TestCase):
    def setUp(self):
        request = Mock()
        request.base_url = 'http://localhost/test'
        request.url = 'http://localhost/test?skip=2&limit=2'
        request.args = Mock()
        request.args.get = Mock(return_value=2)

        paginators.request = request

    def test_paginate(self):
        data = {i: i for i in range(4)}

        p = paginators.Paginator
        p.soft_pagination = False

        content, page = p.paginate(data, 2, 2)
        self.assertEqual(len(content), 2, content)
        self.assertDictEqual(content, {2: 2, 3: 3})

    def test_soft_paginate(self):
        data = {i: i for i in range(4)}

        p = paginators.Paginator
        p.soft_pagination = True

        content, page = p.paginate(data)
        self.assertEqual(len(content), 4)

        self.assertIn('current', page)
        self.assertIn('previous', page)
        self.assertIn('next', page)
        self.assertIn('skip', page)
        self.assertIn('limit', page)
        self.assertIn('count', page)
