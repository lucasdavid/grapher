from flask import Flask
from flask_restful import Api

from . import resources


app = Flask(__name__)
app.config.from_object('demosthenes.settings.ProductionSettings')

api = Api(app)

api.add_resource(resources.HomeResource, '/')

api.add_resource(resources.StudentsResource, '/students')
api.add_resource(resources.StudentResource, '/students/<int:id>')
