from grapher import resources


class User(resources.EntityResource):
    schema = {
        'name': {'type': 'string', 'required': True},
        'age': {'type': 'integer'},
    }


class Group(resources.EntityResource):
    schema = {
        'name': {'type': 'string', 'required': True},
    }


class Members(resources.RelationshipResource):
    origin = Group
    target = User
