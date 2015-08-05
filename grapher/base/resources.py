import abc
from flask_restful import Resource

from . import repositories, paginators, serializers


class BaseResource(Resource):
    @classmethod
    def uri(cls):
        return '/%s' % cls.__name__[:-8].lower()


class ModelResource(BaseResource):
    model = {
        'name': None,
        'verbose-name': None,
        'uri': None,
        'fields': {
            'public': set(),
            'private': set(),
        }
    }

    repository_class = None
    serializer_class = None

    def __init__(self):
        self._serializer = self._repository = self._paginator = None

    @classmethod
    def uri(cls):
        return cls.model['uri'] or super().uri()

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.model)
        return self._repository

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.model)
        return self._serializer

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    def get(self):
        data = self.repository.all()
        data = self.paginator.load(data).paginate()
        data = self.serializer.load(data).serialize()

        return data


class GraphModelResource(ModelResource):
    repository_class = repositories.GraphRepository
    serializer_class = serializers.GraphSerializer
