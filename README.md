# Grapher

[![Build Status](https://travis-ci.org/lucasdavid/grapher.svg?branch=master)](https://travis-ci.org/lucasdavid/grapher)
[![Coverage Status](https://coveralls.io/repos/lucasdavid/grapher/badge.svg?branch=master&service=github)](https://coveralls.io/github/lucasdavid/grapher?branch=master)

## Introduction
RESTful APIs creator based on resource schematics.

Grapher aims at high speed development of high quality web
[RESTFul APIs](https://en.wikipedia.org/wiki/Representational_state_transfer). The idea is to provide a automatic
back-end - just like [eve-python](http://python-eve.org/) -, but without sacrificing the possibility of customization -
similar to [rest-framework](http://www.django-rest-framework.org/).

If your goal is to develop a distributed/web application, take a look at our
[wiki](https://github.com/lucasdavid/grapher/wiki) to see how we can help you!
For now, a glimpse on how is to design APIs with grapher:

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

class Authorship(resources.EntityResource):
    origin = Author
    target = Book
    cardinality = Cardinality.many
    schema = {
        'year': {'type': 'integer'}
    }

```
  
## Contributing

Any contributions are more than welcome. Please refer to
[wiki/contributing](https://github.com/lucasdavid/grapher/wiki/contributing) and the
[issues page](https://github.com/lucasdavid/grapher/issues) to see what needs to be done or make your own suggestions.
