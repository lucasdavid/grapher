# Grapher

## Introduction
Automatic back-end service generator based on resource schematics.

Grapher aims at high speed and high quality development of web
[RESTFul APIs](https://en.wikipedia.org/wiki/Representational_state_transfer). The idea is to provide a automatic
back-end - just like [eve-python](http://python-eve.org/) -, but without sacrificing customization -
 similar to [rest-framework](http://www.django-rest-framework.org/).

## Documentation

 * [docs/SETUP.md](https://github.com/lucasdavid/grapher/blob/master/docs/SETUP.md): provides instructions 
 on how to setup the project for development.
 * [docs/BASICS.md](https://github.com/lucasdavid/grapher/blob/master/docs/BASICS.md): covers the Grapher's basic
 usage, explaining how to declare resources and consume the service.
 * [docs/ADVANCED.md](https://github.com/lucasdavid/grapher/blob/master/docs/ADVANCED.md): covers advanced usage and
  customization of Grapher.

## Testing

Use nose to test the project:
```shell
# Runs all tests inside tests.unit
nosetests

# Runs integration tests
nosetests --tests tests.integration

# Runs everything
nosetests --tests tests

```
