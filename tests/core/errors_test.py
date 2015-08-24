from unittest import TestCase
from grapher.core import errors
from grapher.settings import TestingSettings


class GrapherErrorTest(TestCase):
    def test_internal_error(self):
        e = errors.GrapherError()

        self.assertEqual(e.status_code, 500)
        response = e.as_api_response()

        self.assertIn('INTERNAL_ERROR', response)
        self.assertEqual(len(response), 1)


class BadRequestErrorTest(TestCase):
    def test_valid_error_codes(self):
        valid_errors = (
            'DATA_CANNOT_BE_EMPTY',
            ('DATA_CANNOT_BE_EMPTY',),
            ('NOT_FOUND', (10,),),
            ('INVALID_FIELDS', ('name, age',), ('_id, job',))
        )

        e = errors.BadRequestError(*valid_errors)
        self.assertEqual(e.status_code, 400)

        response = e.as_api_response()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)

        for code, error in response.items():
            self.assertIn(code, TestingSettings.ERRORS)
