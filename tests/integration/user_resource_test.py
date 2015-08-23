import requests
from faker import Faker
from unittest import TestCase

f = Faker()


def fake_user():
    return {
        'name': f.name(),
        'email': f.email(),
        'password': 'root1234!',
    }

BASE_URL = 'http://localhost/%s'


class UserResourceTest(TestCase):
    def test_get(self):
        response = requests.get(BASE_URL % 'user')

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertIn('_meta', response_data)
        self.assertIn('content', response_data)
        self.assertIsInstance(response_data['content'], list)

    def test_post(self):
        data = [fake_user() for _ in range(4)]

        response = requests.post(BASE_URL % 'user', json=data)

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertIn('created', response_data)
        self.assertEqual(len(data), len(response_data['created']))

    def test_put(self):
        response = requests.get(BASE_URL % 'user?limit=1')
        user_id = response.json()['content'][0]['_id']

        user = fake_user()
        user['_id'] = user_id

        response = requests.put(BASE_URL % 'user', json=[user])

        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertIn('updated', response_data)
        self.assertEqual(1, len(response_data['updated']))
        self.assertEqual(user_id, response_data['updated'][0]['_id'])
        self.assertEqual(user['name'], response_data['updated'][0]['name'])
        self.assertEqual(user['email'], response_data['updated'][0]['email'])

    def test_patch(self):
        user = fake_user()

        response = requests.post(BASE_URL % 'user', json=[user])
        user_id = response.json()['created'][0]['_id']

        user['_id'] = user_id
        del user['email']
        del user['password']

        response = requests.patch(BASE_URL % 'user', json=[user])
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        self.assertIn('updated', response_data)
        self.assertEqual(1, len(response_data['updated']))
        self.assertEqual(user_id, response_data['updated'][0]['_id'])
        self.assertEqual(user['name'], response_data['updated'][0]['name'])
