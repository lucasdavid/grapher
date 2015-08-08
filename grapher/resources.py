from .core import resources, filters


class Home(resources.BaseResource):
    end_point = '/'

    def get(self):
        return 'Hello world!'


class User(resources.GraphModelResource):
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 4,
            'identity': True,
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
