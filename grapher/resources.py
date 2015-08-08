from .core import resources, filters


class Home(resources.BaseResource):
    end_point = '/'

    def get(self):
        return 'Hello world!'


class User(resources.GraphModelResource):
    schema = {
        '_id': {
            'identity': True,
            'type': int,
            'protected': True
        },
        'name': {
            'type': str,
            'help': 'The unique identity of a user.',
            'required': True,
            'index': True,
        },
        'email': {
            'type': str,
            'required': False,
            'help': 'A valid email account through which the user can be contacted.',
            'unique': True,
        },
        'password': {
            'type': str,
            'required': True,
            'help': 'The password used by the user to log in the system.',
            'visible': False,
            'protected': False,
        },
    }
