# Grapher [![Build Status](https://travis-ci.org/lucasdavid/grapher.svg?branch=master)](https://travis-ci.org/lucasdavid/grapher)


## Introduction
Automatic back-end service generator based on resource schematics.

Grapher aims at high speed development of high quality web
[RESTFul APIs](https://en.wikipedia.org/wiki/Representational_state_transfer). The idea is to provide a automatic
back-end - just like [eve-python](http://python-eve.org/) -, but without sacrificing the possibility of customization -
similar to [rest-framework](http://www.django-rest-framework.org/).

If your goal is to develop a distributed/web application, take a look at Grapher's docs to see how we can help you! 


## Documentation

 * [docs/SETUP.md](https://github.com/lucasdavid/grapher/blob/master/docs/SETUP.md): provides instructions 
 on how to setup the project for development.
 * [docs/BASICS.md](https://github.com/lucasdavid/grapher/blob/master/docs/BASICS.md): covers the Grapher's basic
 usage, explaining how to declare resources and consume the service.
 * [docs/ADVANCED.md](https://github.com/lucasdavid/grapher/blob/master/docs/ADVANCED.md): covers advanced usage and
  customization of Grapher.
  
## TODO

Any contributions are more than welcome. Please refer to the [issues page](https://github.com/lucasdavid/grapher/issues)
to see what needs to be done or make your own suggestions.

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
