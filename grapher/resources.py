from .core import resources


class User(resources.GraphModelResource):
    description = 'users, such as students, professors and researches.'
    methods = ('GET', 'POST', 'PUT', 'PATCH',)

    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'minlength': 4,
        },
        'email': {
            'type': 'string',
            'required': False,
            'empty': False,
            'index': True,
        },
        'password': {
            'type': 'string',
            'required': True,
            'empty': False,
            'minlength': 6,
            'visible': False,
        },
    }


class Department(resources.GraphModelResource):
    description = 'university\'s departments.'
    methods = ('GET', 'POST',)

    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'minlength': 4,
        }
    }
