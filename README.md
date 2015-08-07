# Grapher

## Introduction
Python automatic back-end generator for model-oriented development.

## Usage
Define your resources inside the **resources.py** file, inheriting from
`BaseResource` or `GraphModelResource` classes.

For example:
```py
class User(resources.GraphModelResource):
    schema = {
        'name': {'type': str},
        'password': {'type': str},
    }
```

You can now access /user and manipulate the resource freely.

Advanced options:
```py
class User(resources.ModelResource):
    end_point = '/users'
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

    # Cannot be defined simultaneously with :protect property.
    expose = ('name', 'email',)
    # Cannot be defined simultaneously with :expose property.
    protect = ('password',)

    repository_class = ...
    serializer_class = ...
```
