from datetime import datetime

import requests
from faker import Faker

RELATIONSHIP = 'founder'
URL = 'http://localhost/%s'
TITLE = 'Grapher example 2: {%s} relationship manipulation.' % RELATIONSHIP

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


def main():
    response = requests.get(URL % 'group')
    assert response.status_code == 200

    groups = response.json()['content']

    response = requests.get(URL % 'user')
    assert response.status_code == 200
    users = response.json()['content']

    # Retrieve each group founder.
    for group in groups:
        response = requests.get(URL % '/group/%i/founder' % group['_id'])
        founder = response.json()['content']

        print('Group #%i\'s founder is:' % group['_id'])
        print(founder)

    # Make sure we have at least one group and one user.
    assert groups and users

    d = {'user': users[0]['_id'], 'since': datetime.now()}

    response = requests.post(URL % 'group/%i/founder' % groups[0]['_id'], json=d)
    founder = response.json()['created']

    print(founder)


if __name__ == '__main__':
    main()
