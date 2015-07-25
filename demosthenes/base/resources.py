from flask import request
from flask_restful import Resource

from .common import Page

custom_data = [{'name': 'user %i' % i, 'id': i} for i in range(1, 10)]


class BaseResource(Resource):
    repository = None


class NodeResource(BaseResource):
    def get(self, id):
        data = self.repository.find(id)

        return data


class CollectionResource(BaseResource):
    def get(self):
        return Page(
            data=custom_data,
            skip=request.args.get('skip'),
            limit=request.args.get('limit')).data
