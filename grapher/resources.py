from .core import resources


class Home(resources.BaseResource):
    end_point = '/'

    def get(self):
        return 'Hello world!'


class User(resources.GraphModelResource):
    schema = {
        'name': {
            'type': str,
            'required': True,
            'help': 'The unique identity of a user.',
        },
        'email': {
            'type': str,
            'required': False,
            'help': 'A valid email account through which the user can be contacted.',
        },
        'password': {
            'type': str,
            'required': True,
            'help': 'The password used by the user to log in the system.',
        },
    }

    protect = ('password',)
