from datetime import datetime
from unittest import TestCase

import requests
from faker import Faker

f = Faker()


def fake_user():
    return {
        'name': f.name(),
        'email': f.email(),
        'password': 'root1234!',
    }


def fake_group():
    return {
        'name': f.text(max_nb_chars=10),
    }


BASE_URL = 'http://localhost/%s'


class FounderRelationshipTest(TestCase):
    def test_post(self):
        response = requests.post(BASE_URL % 'user', json=fake_user())
        self.assertEqual(200, response.status_code)
        user = response.json()['created'].pop()

        group = fake_group()

        response = requests.post(BASE_URL % 'group', json=group)
        self.assertEqual(200, response.status_code)
        group = response.json()['created'].pop()

        d = {'user': group['_id'], 'since': datetime.now()}

        response = requests.post(BASE_URL % 'group/%i/founder' % user['_id'], json=d)
        self.assertEqual(200, response.status_code)
