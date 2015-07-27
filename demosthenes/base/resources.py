from flask_restful import Resource

from . import Paginator, Model, errors
from .serializers import Serializer
from .repositories import Repository


class BaseResource(Resource):
    model = None

    def __init__(self):
        if not issubclass(self.model, Model):
            raise errors.ComponentInstantiationError(self, self.model)

        self.repository = Repository(self.model)


class NodeResource(BaseResource):
    def get(self, id):
        # data = self.repository.find(id)

        return {}


class CollectionResource(BaseResource):
    def get(self):
        data = list(self.repository.all())
        data = Paginator(data=data).paginate()
        data = Serializer(data=data, fields=self.model.public_fields[:]).serialize()

        return data
