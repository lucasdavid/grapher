import inspect
from flask import Flask
from flask_restful import Api

from . import resources as user_resources
from .core import resources, docs

# Initiate API.
app = Flask(__name__)
app.config.from_object('grapher.settings.ProductionSettings')

api = Api(app)


# Scan .grapher.resources after resources declared by the user.
# Finally, build a list of (endpoint, resource) tuples for each resource declared.
rs = [r for name, r in
      inspect.getmembers(user_resources, lambda c: inspect.isclass(c) and issubclass(c, resources.BaseResource))]

for r in rs:
    api.add_resource(r, r.real_end_point())


# Gives all resources scanned to the Docs resource and register it.
docs.Docs.resources_to_describe = rs
api.add_resource(docs.Docs, docs.Docs.real_end_point())
