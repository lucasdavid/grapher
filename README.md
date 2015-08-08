# Grapher

## Introduction
Python automatic back-end generator for model-oriented development.

## How-to
### Basic usage
Define your resources inside the **resources.py** file, inheriting from
`BaseResource`, `ModelResource` or `GraphModelResource` classes.

For example:
```py
from .core import resources

class User(resources.GraphModelResource):
    schema = {
        'name': {'type': str},
        'password': {'type': str},
    }
```

You can now access /user and manipulate the resource freely.

### Advanced usage
#### Available properties
The following class exemplifies the available properties which are considered by the Grapher.

```py
from .core import resources

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

#### Overriding HTTP methods.
If you wish to change the default behavior of a method, simply override it in your resource class:
```py
from .core import resources

class Task(resources.GraphModelResource):
    schema = {
        'title': {'type': str},
        'lead': {'type': str},
    }

    def get(self):
        return 'Hello! You can trust me! I\'m different!'
```
