from .. import resources


class User(resources.EntityResource):
    schema = {
        'username': {
            'type': 'string',
            'required': True,
            'empty': False,
            'minlength': 4
        },
        'email': {
            'type': 'string',
            'required': False,
            'empty': False,
            'index': True
        },
        'password': {
            'type': 'string',
            'required': True,
            'empty': False,
            'minlength': 6,
            'visible': False
        },
    }

    @classmethod
    def initialize(cls):
        super().initialize()


class Group(resources.EntityResource):
    schema = {
        'name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'minlength': 2
        },
    }


class Token(resources.EntityResource):
    schema = {
        'text': {
            'type': 'string',
            'required': True,
            'empty': False,
        }
    }
