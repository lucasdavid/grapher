import inspect

from flask import Flask
from flask_restful import Api

from . import resources as resources_module
from .base.resources import BaseResource

app = Flask(__name__)
app.config.from_object('grapher.settings.ProductionSettings')

api = Api(app)

resources = (r for name, r in
             inspect.getmembers(resources_module, lambda c: inspect.isclass(c) and issubclass(c, BaseResource)))

# Build a list of (endpoint, resource) tuples for each resource declared.
for r in resources:
    api.add_resource(r, isinstance(r.uri, str) and r.uri or r.uri())
