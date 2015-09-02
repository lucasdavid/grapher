from grapher import resources


class User(resources.EntityResource):
    schema = {
        'name': {'type': 'string', 'required': True},
        'age': {'type': 'integer'},
    }
