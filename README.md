# grapher

## Introduction
RESTful APIs creator based on resource schematics.

Grapher aims at high speed development of high quality web
[RESTFul APIs](https://en.wikipedia.org/wiki/Representational_state_transfer). The idea is to provide a automatic
back-end -- just like [eve-python](http://python-eve.org/) -- without sacrificing the possibility of customization --
similar to [rest-framework](http://www.django-rest-framework.org/).

A glimpse on how is to design APIs with grapher:

```py
class Book(resources.EntityResource):
    schema = {
        'title': {'type': 'string', 'required': True},
        'isbn': {'type': 'string'}
    }

class Author(resources.EntityResource):
    schema = {
        'name': {'type': 'string', 'required': True}
    }

class Authorship(resources.RelationshipResource):
    origin = Author
    target = Book
    cardinality = Cardinality.many
    schema = {
        'year': {'type': 'integer'}
    }

```

## Documentation and contributing

All documents were moved to our [wiki](https://github.com/lucasdavid/grapher/wiki). There, you can find posts about concepts used, tecnical usage and guidelines. Any contributions are more than welcome. Please refer to
[wiki/contributing](https://github.com/lucasdavid/grapher/wiki/contributing) and the
[issues page](https://github.com/lucasdavid/grapher/issues) to see what needs to be done or make your own suggestions.
