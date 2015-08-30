import importlib
import flask_restful
from flask import request

from . import settings, serializers, repositories, paginators, errors, commons


class Resource(flask_restful.Resource):
    end_point = name = description = None

    methods = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT', 'DELETE')

    _paginator = None

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    @classmethod
    def real_end_point(cls):
        """Retrieve the resource end-point based on the overwritten property :uri_end_point or on the :real_name() method.

        :return: :str: the string representing the name of the resource.
        """
        end_point = (cls.end_point or cls.real_name()).lower()

        if end_point[0] != '/':
            # Add base slash, if it doesn't have it yet.
            end_point = '/%s' % end_point

        return end_point

    @classmethod
    def real_name(cls):
        """Retrieve the resource's real name based on the overwritten property :name or the class name.

        :return: :str: the name that clearly represents the resource.
        """
        return cls.name or '%s' % cls.__name__

    @classmethod
    def describe(cls):
        return {
            'uri': cls.real_end_point(),
            'description': cls.description or 'resource %s' % cls.real_name(),
            'methods': cls.methods,
        }

    @staticmethod
    def response(content=None, status_code=200, wrap=False, remove_empty_keys=False, **meta):
        result = {}

        if meta:
            result['_meta'] = meta

        if content is not None:
            if remove_empty_keys:
                if not isinstance(content, dict):
                    raise ValueError('Cannot remove empty keys if content is not a dictionary.')

                for k in content.keys():
                    if not content[k]:
                        del content[k]

            if wrap:
                result['content'] = content
            else:
                if isinstance(content, dict):
                    result.update(content)
                elif not meta:
                    # No metadata to add, content is the very whole response.
                    result = content
                else:
                    # There's metadata to add, but the user didn't specified if the content to be wrapped.
                    # Since the content isn't a dictionary, merging isn't possible.
                    raise RuntimeError(
                        'Cannot merge %s into result dictionary. Please define '
                        'content as a dictionary or set wrap to True.' % str(content))

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

    def options(self):
        return self.describe()


class SchematicResource(Resource):
    schema = {}

    repository_class = repositories.Repository
    serializer_class = serializers.DynamicSerializer

    def __init__(self):
        if not self.schema:
            self.schema = {}

        commons.SchemaNavigator.add_identity(self.schema)

    _repository = None

    @property
    def repository(self):
        self._repository = self._repository or self.repository_class(self.real_name(), self.schema)
        return self._repository

    _serializer = None

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.schema)
        return self._serializer

    @classmethod
    def describe(cls):
        d = super().describe()
        d.update(schema=cls.schema)

        return d


class ModelResource(SchematicResource):
    def get(self):
        try:
            d = self.repository.all()
            d, fields = self.serializer.project(d)
            d, page = self.paginator.paginate(d)

            return self.response(d, projection=fields, page=page, wrap=True)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def post(self):
        try:
            entries, declined = self.serializer.validate(request.json)

            entries = self.repository.create(entries)
            entries, fields = self.serializer.project(entries)

            return self.response({'created': entries, 'failed': declined},
                                 remove_empty_keys=True,
                                 projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def put(self):
        try:
            entries, _ = commons.CollectionHelper.transform(request.json)

            # Makes sure every entry has an identity.
            _ = self._get_identities(entries)

            return self._real_update(entries)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def patch(self):
        try:
            r, _ = commons.CollectionHelper.transform(request.json)

            # We need all the entities' data to run meaningful validations.
            entries = self.repository.find(self._get_identities(r))

            # Patches the request data onto the database data.
            for i in range(len(r)):
                entries[i].update(r[i])

            del r

            return self._real_update(entries)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def _get_identities(self, d):
        identity = commons.SchemaNavigator.identity_from(self.schema)
        try:
            return (e[identity] for e in d)

        except KeyError:
            raise errors.BadRequestError('UNIDENTIFIABLE')

    def _real_update(self, entries):
        entries, declined = self.serializer.validate(entries, require_identity=True)

        entries = self.repository.update(entries)
        entries, fields = self.serializer.project(entries)

        return self.response({'updated': entries, 'failed': declined},
                             remove_empty_keys=True,
                             projection=fields)

    def delete(self):
        try:
            entries, fields = self.serializer.project(request.json)

            return self.response({'deleted': entries}, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())


class RelationshipResource(SchematicResource):
    origin = target = None
    cardinality = commons.Cardinality.one

    methods = ('GET',)

    def __init__(self):
        super().__init__()

        if not self.origin or not self.target:
            raise ValueError('Relationship resources must have a valid origin and target attribute set.')

        defined_resources = importlib.import_module('%s.%s' % (settings.effective.BASE_MODULE, 'resources'))

        # If references are strings, import the actual classes.
        if isinstance(self.origin, str):
            self.origin = getattr(self.origin, defined_resources)
        if isinstance(self.target, str):
            self.origin = getattr(self.target, defined_resources)

        # Make sure classes are ModelResource subclass, as they are databases' entities.
        if not issubclass(self.origin, ModelResource):
            raise ValueError(
                'Origin references {%s}. Try a ModelResource subclass instead.' % ModelResource.__name__)
        if not issubclass(self.target, ModelResource):
            raise ValueError(
                'Target references {%s}. Try a ModelResource subclass instead.' % ModelResource.__name__)

        if self.cardinality != '1' and self.cardinality != '*':
            raise ValueError('Cardinality must be "1" or "*" and %s was given.' % str(self.cardinality))

        # Injecting :_origin and :_target properties in schema.
        # They are fundamental as this is a relationship resource.
        identity = commons.SchemaNavigator.identity_from(self.origin.schema)
        self.schema['_origin'] = {
            'required': True,
            'type': identity in self.origin.schema and self.origin.schema[identity]['type'] or 'integer'
        }

        identity = commons.SchemaNavigator.identity_from(self.target.schema)
        self.schema['_target'] = {
            'required': True,
            'type': identity in self.target.schema and self.target.schema[identity]['type'] or 'integer'
        }

    @classmethod
    def real_end_point(cls):
        return '%s/<int:identity>%s' % (cls.origin.real_end_point(), super().real_end_point())

    def get(self, identity):
        try:
            links = self.repository.find_link(origin=identity)
            links, fields = self.serializer.project(links)

            if self.cardinality == commons.Cardinality.one and len(links):
                links = links[0]

            return self.response(links, wrap=True, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    def post(self, identity):
        try:
            links, _ = commons.CollectionHelper.transform(request.json)

            if self.cardinality == commons.Cardinality.one and len(links) > 1:
                raise errors.BadRequestError('CARDINALITY_1_MISMATCH')

            links, declined = self.serializer.validate(links)
            links = self.repository.link(links)
            links, fields = self.serializer.project(links)

            return self.response({'created': links, 'failed': declined}, projection=fields)

        except errors.GrapherError as e:
            return self.response(status_code=e.status_code, errors=e.as_api_response())

    @classmethod
    def describe(cls):
        d = super().describe()
        d.update(
            relationship={
                'origin': cls.origin.real_name(),
                'target': cls.target.real_name(),
                'cardinality': cls.cardinality
            }
        )

        return d


class GraphModelResource(ModelResource):
    repository_class = repositories.GraphRepository


class GraphRelationshipResource(RelationshipResource):
    repository_class = repositories.GraphRepository
