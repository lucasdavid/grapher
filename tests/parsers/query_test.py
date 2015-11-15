from unittest import TestCase
from unittest.mock import Mock

from grapher.parsers import QueryParser
from grapher.parsers import query
from nose_parameterized import parameterized


class QueryParserTest(TestCase):
    def setUp(self):
        r = Mock()
        r.args = Mock()
        r.args.get = Mock()
        query.request = r

    @parameterized.expand([
        (None, {'query': {}, 'skip': 0, 'limit': None}),
        ('{"test":"test 1"}', {'query': {'test': 'test 1'}, 'skip': 0, 'limit': None}),
    ])
    def test_parse(self, request_query, expected):
        query.request.args.get.return_value = request_query

        actual = QueryParser.parse()

        self.assertEqual(actual, expected)
