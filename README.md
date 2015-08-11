# GRAPHER
## Introduction
Automatic back-end service generator based on resource schematics.

## How to use it
### Basic usage
#### Defining schematics
Define your resources inside the **resources.py** file, inheriting from
`BaseResource`, `ModelResource` or `GraphModelResource` classes.

For example:
```py
from .core import resources

class Department(resources.GraphModelResource):
    schema = {
        'name': {'type': 'string'}
    }

```
Schematics are based on the awesome project [cerberus](docs.python-cerberus.org/).
Naturally, all cannonical validation rules apply here.

#### Paginating
You can control the flow of data that you receive.
That's specially convenient when you have a sensible network link.
```shell
curl http://localhost/department?skip=2&take=2
```
```http
content-type: application/json
date: Tue, 11 Aug 2015 01:48:47 GMT
server: Werkzeug/0.10.4 Python/3.4.3
content-length: 534

{
    "content": [
        {
            "_id": 9614,
            "name": "Computer Engineer"
        }
    ],
    "_meta": {
        "page": {
            "next": "http://localhost/department?skip=2&limit=1",
            "previous": "http://localhost/department?skip=0&limit=1",
            "current": "http://localhost/department?skip=1&limit=1",
            "total": 3,
            "count": 1,
            "limit": 1,
            "skip": 1
        },
        "projection": [
            "name",
            "_id"
        ]
    }
}
```

#### Projecting
You can select properties from the resources, consisely reducing the responses sizes.
```shell
curl http://localhost/department?fields=id
```
```http
content-type: 'application/json'
date: 'Tue, 11 Aug 2015 01:50:57 GMT
server: Werkzeug/0.10.4 Python/3.4.3
content-length: 479

{
    "content": [
        {
            "_id": 9613
        },
        {
            "_id": 9614
        },
        {
            "_id": 9615
        }
    ],
    "_meta": {
        "page": {
            "next": null,
            "previous": null,
            "current": "http://localhost/department?fields=_id",
            "total": 3,
            "count": 3,
            "limit": 3,
            "skip": 0
        },
        "projection": [
            "_id"
        ]
    }
}
```

Done! You can now access `/user` and manipulate the resource freely!

### Further use
#### Available properties
The following class exemplifies the available properties which are considered by the Grapher.

```py
from .core import resources, repositories, serializers

class User(resources.ModelResource):
    end_point = '/users'
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

#### Taking control over the code-flow
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
		d, fields = self.serializer.project(d)
		
        return self.response(d, projection=fields)
```
