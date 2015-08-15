import flask_restful
from flask import request
from cerberus import SchemaError

from . import serializers, repositories, paginators, errors


class Resource(flask_restful.Resource):
    end_point = name = description = None

    methods = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT', 'DELETE')

    @classmethod
    def real_end_point(cls):
        """Retrieve the resource end-point based on the overwritten property :uri_end_point or on the :clean_name() method.

        :return: :str: the string representing the name of the resource.
        """
        end_point = cls.end_point or cls.clean_name().lower()

        if end_point[0] != '/':
            # Add base slash, if it doesn't have it yet.
            end_point = '/%s' % end_point

        return end_point

    @classmethod
    def clean_name(cls):
        """Retrieve a clean name for the resource based on the overwritten property :name or on class name.

        :return: :str: the name that clearly represents the resource.
        """
        return cls.name or '%s' % cls.__name__

    @staticmethod
    def response(content={}, status_code=200, **meta):
        result = {}

        if meta:
            result['_meta'] = meta

        if isinstance(content, dict):
            result.update(content)
        else:
            result['content'] = content

        return result, status_code

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


class ModelResource(Resource):
    schema = {}

    repository_class = repositories.Repository
    serializer_class = serializers.DynamicSerializer

    def __init__(self):
        if not self.schema:
            raise SchemaError('Schema is an essential part of a model-resource.'
                              'Define a valid schema or change %s to inherit from base-resource.'
                              % self.clean_name())

        identity_field = None
        for field, description in self.schema.items():
            if 'identity' in description and description['identity']:
                identity_field = field

        if identity_field is None:
            self.schema['_id'] = {
                'type': 'integer',
                'identity': True,
            }

    _repository = None

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.clean_name(), self.schema)
        return self._repository

    _serializer = None

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.schema)
        return self._serializer

    _paginator = None

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    def get(self):
        try:
            d = self.repository.all()
            d, fields = self.serializer.project(d)
            d, page = self.paginator.paginate(d)

            return self.response(d, projection=fields, page=page)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def post(self):
        try:
            entries, declined = self.serializer.validate(request.json)

            entries = self.repository.create(entries)
            entries, fields = self.serializer.project(entries)

            return self.response({'created': entries, 'failed': declined}, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def put(self):
        try:
            entries, declined = self.serializer.validate(request.json)

            entries = self.repository.update(entries)
            entries, fields = self.serializer.project(entries)

            return self.response({'updated': entries, 'failed': declined}, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def patch(self):
        try:
            entries, declined = self.serializer.validate(request.json, accept_partial_data=True)

            entries = self.repository.update(entries)
            entries, fields = self.serializer.project(entries)

            return self.response({'updated': entries, 'failed': declined}, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def delete(self):
        try:
            entries, fields = self.serializer.project(request.json)

            return self.response({'deleted': entries}, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())


class RelationshipResource(ModelResource):
    pass


class GraphModelResource(ModelResource):
    repository_class = repositories.GraphRepository


class GraphRelationshipResource(RelationshipResource):
    repository_class = repositories.GraphRepository
