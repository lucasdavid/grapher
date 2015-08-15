# Advanced

## Introduction
This file covers **Grapher** advanced usage.

## Available properties for resources
The following class exemplifies the available properties which are considered by the Grapher.

```py
from .core import resources, repositories, serializers

class User(resources.ModelResource):
    name = 'CustomUser'
    description = 'User\'s resource custom description'
    end_point = 'custom-users'
    
    # Methods supported by Resource.
    methods = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT', 'DELETE')
    
    # Persistence schema.
    schema = {
        'name': {
            'type': str,
            'required': True,
            'help': 'The unique identity of a user.',
			'identity': True,
        },
        'email': {
            'type': str,
            'required': False,
            'help': 'A valid email account through which the user can be contacted.',
			'index': True,
        },
        'password': {
            'type': str,
            'required': True,
            'help': 'The password used by the user to log in the system.',
			'visible': False,
        },
    }

    repository_class = serializers.DynamicSerializer
    serializer_class = serializers.GraphRepository
```

## Taking control over the code-flow
If you wish to change the default behavior, you can do it by simply overriding your **resource class** correspondent method.
```py
from flask_restful import request
from .core import resources

class Task(resources.GraphModelResource):
    schema = {
        'title': {'type': str},
        'lead': {'type': str},
    }
	
    def get(self):
		identity = request.args.get('identity')
		
		# Never raise 404. If task doesn't exist, create it.
		task = self.repository.find(identity) or self.repository.create({})
        
		# Serialize data, preventing sensible data to be sent to clients.
		task, fields = self.serializer.project(task)
		
        return self.response(task, projection=fields)

```

## Using other databases

It's perfectly plausible if you don't think Neo4J is the ideal database for your problem. In that case, just create a 
`repositories.py` file in `grapher` and implement the interface `grapher.core.repositories.Repository`. For example,
let's say you want to use [MongoDB](https://www.mongodb.org/):

```py
from .core import repositories

class MongoRepository(repositories.Repository):
    def all(self, skip=0, limit=None):
        [...]

    def find(self, identity):
        [...]

    def where(self, **query):
        [...]

    def create(self, entities):
        [...]

    def update(self, entities):
        [...]

    def delete(self, entities):
        [...]

```

Finally, just implement a `ModelResource` which refers to this repository:
```py
from .core import resources
from . import repositories

class Department(resources.ModelResource)
    schema = {...}

    repository_class = repositories.MongoRepository

```

The `Department` resource is now handled by `MongoRepository`,
which means its persistence is made by in a MongoDB database.


## Events
Define a method with the name `('before_'|'after_').('create'|'update'|'delete')` in your resource. 
The method will be called when the event get triggered.

```py
from datetime import datetime
from .core import resources
from [...] import Archives

class Task(resources.GraphModelResource):
    schema = {
        'title': {'type': str},
        'lead': {'type': str},
    }
	
	def before_create(self, *args, **kwargs):
		"""I'll be executed before an entity's creation!
		"""
		entities = kwargs.get('entities')
		for entity in entities:
			entity['created_at'] = datetime.now()
	
	def after_delete(self, *args, **kwargs):
		"""All deleted entities are copied to an archive, such as files, mails or other databases.
		"""
		deleted_entities = kwargs.pop('entities')
		Archives.archive('me', body=deleted_entities)

```

A valid event listener is any combination `(prefix + '_' + suffix)` from the two lists bellow:

**Prefixes**
```
before
after
```

**Suffixes**
```
create
update
delete
retrieve
```
