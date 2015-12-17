from .. import resources
from . import managers

from ..commons import Cardinality


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

    manager_class = managers.UserManager

    @classmethod
    def initialize(cls):
        super().initialize()


class Client(resources.EntityResource):
    schema = {
        'name': {'type': 'string', 'required': True, 'empty': False,
                 'maxlength': 40},
        'description': {'type': 'string', 'required': True, 'empty': False,
                        'maxlength': 400},
        'secret': {'type': 'string', 'required': True, 'empty': False,
                   'maxlength': 55, 'unique': True},
        'confidential': {'type': 'boolean', 'default': True},
        'redirect_uris': {'type': 'list', 'schema': {'type': 'string'}},
        'default_scopes': {'type': 'list', 'schema': {'type': 'string'}}
    }

    manager_class = managers.ClientManager


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
        },
        'type': {'type': 'string', 'maxlength': 40},
        'access_token': {'type': 'string', 'maxlength': 255, 'required': True,
                         'empty': False},
        'refresh_token': {'type': 'string', 'maxlength': 255, 'required': True,
                          'empty': False},
        'expires_in': {'type': 'datetime'},
        'scopes': {'type': 'list', 'schema': {'type': 'string'}}
    }


class Grant(resources.EntityResource):
    schema = {
        'code': {'type': 'string', 'maxlength': 255, 'required': True,
                 'empty': False},
        'redirect_uri': {'type': 'string'},
        'expires_in': {'type': 'datetime'},
        'scopes': {'type': 'list', 'schema': {'type': 'string'}}
    }

    manager_class = managers.GrantManager


class ClientGrants(resources.RelationshipResource):
    origin = Client
    target = Grant

    cardinality = Cardinality.one_to_many


class ClientOwner(resources.RelationshipResource):
    origin = User
    target = Client


class GrantOwner(resources.RelationshipResource):
    origin = User
    target = Grant

    cardinality = Cardinality.one


class ClientTokens(resources.RelationshipResource):
    origin = Client
    target = Token

    cardinality = Cardinality.one_to_many


class UserToken(resources.RelationshipResource):
    origin = User
    target = Token

    cardinality = Cardinality.one
