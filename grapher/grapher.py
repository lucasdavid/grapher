import inspect

import importlib
from flask import Flask
from flask_restful import Api
from . import resources, docs, settings


class Grapher:
    instance = None

    def __init__(self, name='Grapher'):
        """Starts Grapher API.

        The instantiation of the class Grapher also creates a flask app and a RESTFul api.

        :param name: the name of the application that will be created.
        """
        if Grapher.instance is not None:
            raise RuntimeError('Grapher is already running.')

        self.settings = settings.effective

        self.app = Flask(name)
        self.app.config.from_object(self.settings)

        self.api = Api(self.app)

        # Start the API, loading all resources and documenting itself.
        rs = self._scan_resources()
        for r in rs:
            if not r.initialized:
                r.initialize()

            self.api.add_resource(r, r.real_end_point())

        # Gives all resources scanned to the Docs resource and register it.
        docs.Docs.resources_to_describe = rs
        self.api.add_resource(docs.Docs, docs.Docs.real_end_point())

        Grapher.instance = self

    def _scan_resources(self):
        """Scan project after subclasses of :Resource declared by the user.
        Then register them in the API.

        All resources must have been declared in .grapher.resources,
        as it's the only module scanned.
        """
        if self.settings.BASE_MODULE is None:
            raise ValueError('effective.BASE_MODULE is not set.')

        declared_resources = '.'.join([self.settings.BASE_MODULE, 'resources'])
        declared_resources = importlib.import_module(declared_resources)

        return [
            r for name, r in inspect.getmembers(
                    declared_resources,
                    lambda c:
                    inspect.isclass(c) and
                    issubclass(c, resources.Resource))
            ]
