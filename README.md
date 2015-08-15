# Grapher

## Introduction
Automatic back-end service generator based on resource schematics.

This project is strongly inspired by
[rest-framework](http://www.django-rest-framework.org/) and [eve-python](http://python-eve.org/).

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
