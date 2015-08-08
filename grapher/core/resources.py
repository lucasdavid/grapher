from flask import request
from flask_restful import Resource, marshal

from . import serializers, validators, repositories, paginators

from .. import settings


class BaseResource(Resource):
    end_point = None
    name = None

    @classmethod
    def real_end_point(cls):
        """Retrieve the resource end-point based on the overwritten property :uri_end_point or on the :clean_name() method.

        :return: :str: the string representing the name of the resource.
        """
        return cls.end_point or '/%s' % cls.clean_name().lower()

    @classmethod
    def clean_name(cls):
        """Retrieve a clean name for the resource based on the overwritten property :name or on class name.

        :return: :str: the name that clearly represents the resource.
        """
        return cls.name or '%s' % cls.__name__

    @staticmethod
    def result(content, **metadata):
        return {
            'content': content,
            '_metadata': metadata
        }


class ModelResource(BaseResource):
    schema = {}

    repository_class = None
    serializer_class = None

    validators = (validators.NotSupportedFields, validators.CorrectFieldTypes,)

    def __init__(self):
        self._repository = self._serializer = self._paginator = None

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.clean_name(), self.schema)
        return self._repository

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.schema)
        return self._serializer

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    def get(self):
        d = self.repository.all()
        d, fields = self.serializer.project(d)
        d, page = self.paginator.paginate(d)

        return self.result(d, projection=fields, page=page)

    def post(self):
        accepted, declined = self.serializer.digest(request.json)

        accepted = self.repository.create(accepted.values())
        accepted, fields = self.serializer.project(accepted)

        return self.result({
            'created': {i: entity for i, entity in enumerate(accepted)},
            'failed': declined
        }, projection=fields)


class GraphModelResource(ModelResource):
    repository_class = repositories.GraphRepository
    serializer_class = serializers.GraphSerializer
