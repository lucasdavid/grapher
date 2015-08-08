from flask import request
from flask_restful import Resource

from . import serializers, repositories, paginators, common


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
    def response(content, **meta):
        result = {}

        if meta:
            result['_meta'] = meta

        if isinstance(content, dict):
            result.update(content)
        else:
            result['content'] = content

        return result

    def _trigger(self, event, *args, **kwargs):
        """Triggers a specific event, in case it has been defined.

        :param event: the event to be triggered.
        :param args: positional arguments passed to the event.
        :param kwargs: key arguments passed to the event.
        :return: the event's result, in case it has been defined.
        """
        method = getattr(self, event)
        if method:
            return method(*args, **kwargs)


class ModelResource(BaseResource):
    schema = {}
    meta = {}

    repository_class = None
    serializer_class = None

    def __init__(self):
        self._repository = self._serializer = self._paginator = None

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.clean_name(), self.schema)
        return self._repository

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.schema, self.meta)
        return self._serializer

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    def get(self):
        d = self.repository.all()
        d, fields = self.serializer.project(d)
        d, page = self.paginator.paginate(d)

        return self.response(d, projection=fields, page=page)

    def post(self):
        entries, declined = self.serializer.validate_or_abort_if_empty(request.json)

        entries = self.repository.create(entries)
        entries, fields = self.serializer.project(entries)

        return self.response({'created': entries, 'failed': declined}, projection=fields)

    def put(self):
        entries, declined = self.serializer.validate_or_abort_if_empty(request.json)

        entries = self.repository.update(entries)
        entries, fields = self.serializer.project(entries)

        return self.response({'updated': entries, 'failed': declined}, projection=fields)


class GraphModelResource(ModelResource):
    repository_class = repositories.GraphRepository
    serializer_class = serializers.GraphSerializer
