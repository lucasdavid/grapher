from unittest import TestCase
from unittest.mock import Mock
from nose_parameterized import parameterized

from grapher import errors
from grapher.parsers import query, RequestQueryParser


class RequestQueryParserTest(TestCase):
    def setUp(self):
        r = Mock()
        r.args = Mock()
        r.args.get = Mock()
        query.request = r

    @parameterized.expand([
        (None, ''),
        ('', ''),
        ('{"test":"test 1"}', '{"test":"test 1"}'),
    ])
    def test_query(self, request_query, expected):
        query.request.args.get.return_value = request_query

        actual = RequestQueryParser.query()

        self.assertEqual(actual, expected)

    @parameterized.expand([
        (None, {}),
        ('{"name":"Test"}', {"name": "Test"}),
    ])
    def test_query_as_object(self, request_query, expected):
        query.request.args.get.return_value = request_query

        actual = RequestQueryParser.query_as_object()

        self.assertDictEqual(actual, expected)

    @parameterized.expand([
        ('{}{}{}',),
        ('{"$xor":{}}',),
    ])
    def test_query_as_object_raise_graph_error(self, request_query):
        query.request.args.get.return_value = request_query

        with self.assertRaises(errors.BadRequestError):
            RequestQueryParser.query_as_object()
