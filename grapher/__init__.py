import inspect
from flask import Flask
from flask_restful import Api

from . import resources as custom_resources
from .core import resources, docs


class Grapher(Flask):
    """Grapher flask application.

    Usage:
        app = Grapher(__name__)
        api = GrapherApi(app).startup()
        app.run()
    """


class GrapherApi(Api):
    def _auto_load_resources(self):
        """Scan project after subclasses of :Resource declared by the user. Then register them in the API.

        All resources must have been declared in .grapher.resources, as it's the only module scanned.
        """
        rs = [r for name, r in inspect.getmembers(custom_resources,
                                                  lambda c: inspect.isclass(c) and issubclass(c, resources.Resource))]
        for r in rs:
            self.add_resource(r, r.real_end_point())

        return self

    def startup(self):
        """Start the API, loading all resources and documenting itself.
        """
        self._auto_load_resources()

        # Gives all resources scanned to the Docs resource and register it.
        docs.Docs.resources_to_describe = (r for r, *_ in self.resources)
        self.add_resource(docs.Docs, docs.Docs.real_end_point())

        return self
