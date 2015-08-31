from datetime import datetime

import requests
from faker import Faker

RELATIONSHIP = 'members'
URL = 'http://localhost/%s'
TITLE = 'Grapher example 2: {%s} relationship manipulation.' % RELATIONSHIP

f = Faker()


def main():
    d = [
        {'_target': 0, 'since': datetime.now().isoformat()},
        {'_target': 1, 'since': datetime.now().isoformat()},
    ]

    response = requests.post(URL % 'group/3/members', json=d)

    print(response.headers)
    print(response.text)
    print(response.json())


if __name__ == '__main__':
    main()
