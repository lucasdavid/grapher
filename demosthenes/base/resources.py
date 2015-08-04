from flask_restful import Resource

from . import repositories, paginators, serializers


class BaseResource(Resource):
    model = None

    def __init__(self):
        self._serializer = self._repository = self._paginator = None

    @property
    def repository(self):
        self._repository = self._repository or repositories.GraphRepository(self.model)
        return self._repository

    @property
    def serializer(self):
        self._serializer = self._serializer or serializers.GraphSerializer(self.model)
        return self._serializer

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator


class NodeResource(BaseResource):
    def get(self, identity):
        data = self.repository.find(identity)
        data = self.serializer.load(data).serialize()

        return data


class CollectionResource(BaseResource):
    def get(self):
        data = self.repository.all()
        data = self.paginator.load(data).paginate()
        data = self.serializer.load(data).serialize()

        return data
