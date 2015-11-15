from unittest import TestCase
from unittest.mock import Mock

from grapher import errors
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
        ({},
         {'query': {}, 'skip': 0, 'limit': None}),
        ({'skip': '2'},
         {'query': {}, 'skip': 2, 'limit': None}),
        ({
             'query': '{"test":"test 1"}',
             'skip': '0',
             'limit': '10'
         },
         {'query': {'test': 'test 1'}, 'skip': 0, 'limit': 10}),
    ])
    def test_parse(self, request_query, expected):
        query.request.args.get.side_effect = lambda e: request_query[e] if e in request_query else None

        actual = QueryParser.parse()

        self.assertEqual(actual, expected)

    def test_invalid_query(self):
        query.request.args.get.return_value = 'invalid$query:{{{}'

        with self.assertRaises(errors.BadRequestError):
            QueryParser.parse()
