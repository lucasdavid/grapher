from .core import resources, filters


class User(resources.GraphModelResource):
    description = 'users, such as students, professors and researches.'
    methods = ('GET', 'POST',)

    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 4,
        },
        'email': {
            'type': 'string',
            'required': False,
            'index': True,
            'visible': False
        },
        'password': {
            'type': 'string',
            'required': True,
            'minlength': 6,
        },
    }


class Department(resources.GraphModelResource):
    description = 'university\'s departments.'
    methods = ('GET', 'POST',)

    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'blank': False,
            'minlength': 4,
        }
    }
