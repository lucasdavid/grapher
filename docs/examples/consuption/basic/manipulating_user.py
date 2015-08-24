import requests
from faker import Faker

RESOURCE = 'user'
URL = 'http://localhost/%s' % RESOURCE
TITLE = 'Grapher example 1: {%s} resource manipulation.' % RESOURCE

f = Faker()


def fake_user():
    return {
        'name': f.name(),
        'email': f.email(),
        'password': 'root1234!',
    }


def main():
    print(TITLE)

    response = requests.get(RESOURCE)
    assert response.status_code == 200

    result = response.json()

    users = result['content']
    print('%i users retrieved.' % result['_meta']['count'])
    print(users)

    # Creating users.
    # Make a list of users with fake data.
    data = [fake_user() for _ in range(4)]

    # Requests users creation.
    response = requests.post(URL, json=data)
    assert response.status_code == 200

    result = response.json()
    users = result['created']

    print('Users %s were created' % str((user['_id'] for user in users)))


if __name__ == '__main__':
    main()
