import py2neo

from flask import Flask
from flask_restful import Api

from . import resources
from . import settings


app = Flask(__name__)
app.config.from_object('demosthenes.settings.ProductionSettings')

py2neo.authenticate(
    settings.ProductionSettings.DATABASES['default']['url'],
    settings.ProductionSettings.DATABASES['default']['username'],
    settings.ProductionSettings.DATABASES['default']['password'])

api = Api(app)

api.add_resource(resources.HomeResource, '/')

api.add_resource(resources.StudentsResource, '/students')
api.add_resource(resources.StudentResource, '/students/<int:id>')
