import importlib
import flask_restful
from flask import request

from . import settings, serializers, repositories, paginators, errors, commons


class Resource(flask_restful.Resource):
    """Grapher's base RESTFul resource.

    Sub-classes of this declared in {project}.resources module
    are automatically loaded as resources.
    """
    end_point = name = description = None

    methods = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT', 'DELETE')

    _paginator = None

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    @classmethod
    def real_name(cls):
        """Retrieve the resource's real name based on the overwritten property :name or the class name.

        :return: :str: the name that clearly represents the resource.
        """
        return cls.name or '%s' % cls.__name__

    @classmethod
    def real_end_point(cls):
        """Retrieve the resource end-point based on its end-point or name.

        :return: :str: the string representing the name of the resource.
        """
        end_point = (cls.end_point or cls.real_name()).lower()

        end_point = '/' + end_point if end_point[0] != '/' else end_point
        end_point = end_point + '/' if end_point[-1] != '/' else end_point

        return end_point

    @classmethod
    def describe(cls):
        return {
            'uri': cls.real_end_point(),
            'description': cls.description or 'resource %s' % cls.real_name(),
            'methods': cls.methods,
        }

    @staticmethod
    def response(content=None, status=200, wrap=True, **meta):
        result = {}

        if meta:
            result['_meta'] = meta

        if content is not None:
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

        return result, status

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

    repository_class = repositories.base.Repository
    serializer_class = serializers.DynamicSerializer

    def __init__(self):
        super().__init__()

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

    def describe(self):
        d = super().describe()
        d.update(schema=self.schema)

        return d

    def _identify(self, entries):
        identity = commons.SchemaNavigator.identity_from(self.schema)

        try:
            return (e[identity] for e in entries)

        except KeyError:
            raise errors.BadRequestError('UNIDENTIFIABLE')

    def _create(self, entries):
        entries, declined = self.serializer.validate(entries)
        entries = self.repository.create(entries)
        entries, fields = self.serializer.project(entries)

        return self.response({'created': entries, 'failed': declined}, wrap=False, projection=fields)

    def _update(self, entries):
        entries, declined = self.serializer.validate(entries, require_identity=True)
        entries = self.repository.update(entries)
        entries, fields = self.serializer.project(entries)

        return self.response({'updated': entries, 'failed': declined}, wrap=False, projection=fields)


class EntityResource(SchematicResource):
    repository_class = repositories.GraphEntityRepository

    def __init__(self):
        super().__init__()

        assert issubclass(self.repository_class, repositories.base.EntityRepository)

    def get(self):
        try:
            d = self.repository.all()
            d, fields = self.serializer.project(d)
            d, page = self.paginator.paginate(d)

            return self.response(d, projection=fields, page=page)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def post(self):
        try:
            entries, _ = commons.CollectionHelper.transform(request.json)
            return self._create(entries)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def put(self):
        try:
            entries, _ = commons.CollectionHelper.transform(request.json)
            # Makes sure every entry has an identity.
            self._identify(entries)

            return self._update(entries)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def patch(self):
        try:
            r, _ = commons.CollectionHelper.transform(request.json)

            # We need all the entities' data to run meaningful validations.
            identities = self._identify(r)
            entries = self.repository.find(identities)

            # Patches the request data onto the database data.
            for i in range(len(r)):
                entries[i].update(r[i])
            del r

            return self._update(entries)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    def delete(self):
        try:
            identities, _ = commons.CollectionHelper.transform(request.json)

            entries = self.repository.delete(identities)
            entries, fields = self.serializer.project(entries)

            return self.response({'deleted': entries}, projection=fields, wrap=False)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())


class RelationshipResource(SchematicResource):
    origin = target = None
    cardinality = commons.Cardinality.one

    repository_class = repositories.GraphRelationshipRepository

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
        if not issubclass(self.origin, EntityResource):
            raise ValueError(
                'Origin references {%s}. Try a ModelResource subclass instead.' % EntityResource.__name__)
        if not issubclass(self.target, EntityResource):
            raise ValueError(
                'Target references {%s}. Try a ModelResource subclass instead.' % EntityResource.__name__)

        if self.cardinality != '1' and self.cardinality != '*':
            raise ValueError('Cardinality must be "1" or "*" and %s was given.' % str(self.cardinality))

        # Injecting :_origin and :_target properties in schema.
        # They are fundamental as this is a relationship resource.
        identity = commons.SchemaNavigator.add_identity(self.origin.schema)
        self.schema['_origin'] = {
            'required': True,
            'type': self.origin.schema[identity]['type']
        }

        identity = commons.SchemaNavigator.add_identity(self.target.schema)
        self.schema['_target'] = {
            'required': True,
            'type': self.target.schema[identity]['type']
        }

        assert issubclass(self.repository_class, repositories.base.RelationshipRepository)

    @classmethod
    def real_end_point(cls):
        identity = commons.SchemaNavigator.add_identity(cls.origin.schema)
        t = cls.origin.schema[identity]['type']

        if t == 'integer':
            t = 'int'

        return '%s<%s:identity>%s' % (cls.origin.real_end_point(), t, super().real_end_point())

    def describe(self):
        d = super().describe()
        d.update(
            relationship={
                'origin': self.origin.real_name(),
                'target': self.target.real_name(),
                'cardinality': self.cardinality
            }
        )

        return d

    def get(self, identity):
        try:
            relationships = self.repository.match(origin=identity)
            relationships, fields = self.serializer.project(relationships)

            if self.cardinality == commons.Cardinality.one:
                if not relationships:
                    raise errors.NotFoundError(('NOT_FOUND', '%s/%s' % (identity, self.real_name())))

                relationships = relationships.pop()

            return self.response(relationships, projection=fields)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    def post(self, identity):
        try:
            relationships, _ = commons.CollectionHelper.transform(request.json)

            if self.cardinality == commons.Cardinality.one and len(relationships) > 1:
                raise errors.BadRequestError('CARDINALITY_1_MISMATCH')

            for l in relationships:
                # Origins are always constrained to the uri's parameters.
                l['_origin'] = identity

            return self._create(relationships)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    def put(self, identity):
        try:
            entries, _ = commons.CollectionHelper.transform(request.json)
            for d in entries:
                d['_origin'] = identity

            # Makes sure every entry has an identity.
            self._identify(entries)

            return self._update(entries)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def patch(self, identity):
        try:
            r, _ = commons.CollectionHelper.transform(request.json)
            for d in r:
                d['_origin'] = identity

            # We need all the entities' data to run meaningful validations.
            identities = self._identify(r)
            entries = self.repository.find(identities)

            # Patches the request data onto the database data.
            for i in range(len(r)):
                entries[i].update(r[i])
            del r

            return self._update(entries)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    def delete(self, identity):
        try:
            identities, _ = commons.CollectionHelper.transform(request.json)

            entries = self.repository.delete(identities)
            entries, fields = self.serializer.project(entries)

            return self.response({'deleted': entries}, projection=fields, wrap=False)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())
