# Basics

## Introduction
This file covers **Grapher** basics, such as models creation, projecting and paginating. 
If you haven't setup the project yet, go over the step-stones in 
[SETUP.md](https://github.com/lucasdavid/grapher/blob/master/docs/SETUP.md) file.

## Configuring and running

On [grapher/settings.py](https://github.com/lucasdavid/grapher/blob/master/grapher/settings.py), fill
`DevelopmentSettings.DATABASES` with your database's appropriate credentials.

Use the `manage.py` to create a instance of a server.
```shell
python manage.py runserver
```
*Please notice that this setup is UNSUITABLE for production.*

## Defining basic models

Grapher is built over the concept of [REST](https://en.wikipedia.org/wiki/Representational_state_transfer). 
Each model created is exposed as a API Resource, which will be consumed by client-side applications, 
such as web pages, mobile applications or other web services.

In order to define a model, simply go to the grapher/resources.py file and declare a subclass of `GraphModelResource`:

```py
class Post(resources.GraphModelResource):
    schema = {
        'title': {'type': 'string'},
        'lead': {'type': 'string', 'minlength': 4},
        'body': {'type': 'string', 'minlength': 4},
    }

```

Done! You don't even have to restart the server. You can access [http://localhost/post](http://localhost/post), which
is the default end-point to where this resource were mapped.

You can switch the end-point, of course:

```py
from .core import resources

class Department(resources.GraphModelResource):
    end_point = '/nice-departments'
    schema = {
        'name': {'type': 'string'}
    }

```

Use [http://localhost/nice-departments](http://localhost/nice-departments) to manipulate the resource.

Note: schematics are based on the awesome project [cerberus](docs.python-cerberus.org/).
Naturally, all canonical validation rules apply here.
Please refer to their documentation when writing your own schematics.

## Interacting with resources
### Creating
After defining your RESTFul resources, your back-end is ready to accept interaction from front-end applications.
For instance, you can create a new Department by sending a [POST request](https://en.wikipedia.org/wiki/POST_(HTTP))
to `nice-departments` end-point.
```shell
curl -X POST http://localhost/nice-departments --data='{"name":"Computer Science"}'
```

Another example: if you have a client python app, with the [requests](http://www.python-requests.org/en/latest/) 
library:
```py
import requests

data = {'name': 'Computer Science'}
response = requests.post('http://localhost/nice-departments', json=data)

assert response.status_code == 200
data = response.json()
department = data['created']

print('Department #%i: %s' % (department['_id'], department['name']))

# I also accept lists for fast insertions!
data = [{'name': 'Department %i' % i} for i in range(10)]
response = requests.post('http://localhost/nice-departments', json=data)

assert response.status_code == 200
data = response.json()

for department in data['created']:
    # List the ID of each department created.
    print(department['_id'])

```
### Updating
You can use the **PATCH** and **PUT** methods to update your resources.

```py
import requests

# Requests all departments (return a list with, at most, two elements).
response = requests.get('http://localhost/nice-departments?limit=2')
data = response.json()

departments = data['content']
names = ['Psychology', 'Computer Science']

for i, department in enumerate(departments):
    # Update each department's name.
    department['name'] = names[i]

# Requests patch over departments.
response = requests.put('http://localhost/nice-departments', json=departments)
assert response.status_code == 200

```

### Deleting

```py
import requests

# Requests all departments (return a list with, at most, two elements).
response = requests.get('http://localhost/nice-departments?limit=2')
data = response.json()
departments = data['content']
ids = [d['_id'] for d in departments]
ids = ','.join(ids)

# Requests deletion of all departments that have one of those IDs.
response = requests.delete('http://localhost/nice-departments?where={"_id__in":%s}' % ids)
assert response.status_code == 200

```

### Paginating
You can control the flow of data that you receive.
That's specially convenient when you have a fragile internet link.

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
        "projection": ["name", "_id"]
    }
}
```

## Projecting
You can select properties from the resources, reducing considerably the responses sizes.

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
        {"_id": 9613},
        {"_id": 9614},
        {"_id": 9615}
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
        "projection": ["_id"]
    }
}
```
