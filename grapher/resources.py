from .core import resources


class User(resources.GraphModelResource):
    end_point = 'users'
    description = 'users, such as students, professors and researches.'

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False, 'minlength': 4},
        'email': {'type': 'string', 'required': False, 'empty': False, 'index': True},
        'password': {'type': 'string', 'required': True, 'empty': False, 'minlength': 6, 'visible': False},
    }


class Group(resources.GraphModelResource):
    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False, 'minlength': 2},
        'members': {
            'type': 'list',
            'relationship': {
                'resource': 'User',
                'schema': {
                    'created_at': {'type': 'datetime'}
                },
            },

        },
    }


class Membership(resources.GraphRelationshipResource):
    schema = {
        'user': {'relationship': 'User'},
        'group': {'relationship': 'Group'},
    }


class Department(resources.GraphModelResource):
    description = 'university\'s departments.'

    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False, 'minlength': 4},
        'adviser': {'relationship': 'User'},
        'professors': {
            'type': 'list',
            'schema': {'relationship': 'User'}
        },
    }
