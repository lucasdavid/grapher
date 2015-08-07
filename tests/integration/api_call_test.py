import requests

from unittest import TestCase


class StudentsResourceTest(TestCase):
    def test_post(self):
        data = {
            'username': 'ldavid',
            'password': 'root',
        }

        result = requests.post('http://localhost/students', data=data)

        self.assertEqual(result.status_code, 200)
