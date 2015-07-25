from flask_restful import Resource

from .base.resources import NodeResource, CollectionResource


class HomeResource(Resource):
    def get(self):
        return {}


class StudentsResource(CollectionResource):
    pass


class StudentResource(NodeResource):
    pass
