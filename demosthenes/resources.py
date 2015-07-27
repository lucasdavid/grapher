from flask_restful import Resource

from . import models
from .base import NodeResource, CollectionResource


class HomeResource(Resource):
    def get(self):
        return 'Hello world!'


class StudentsResource(CollectionResource):
    model = models.Student


class StudentResource(NodeResource):
    model = models.Student
