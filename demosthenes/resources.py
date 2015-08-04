import flask_restful

from . import models
from .base import resources


class HomeResource(flask_restful.Resource):
    def get(self):
        return 'Hello world!'


class StudentsResource(resources.CollectionResource):
    model = models.Student


class StudentResource(resources.NodeResource):
    model = models.Student
