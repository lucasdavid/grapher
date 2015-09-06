import importlib
from flask_restful import request

from .base import Resource
from .. import repositories, serializers, parsers, commons, settings, errors


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
        self._repository = self._repository or self.repository_class(self.real_name(), self.schema, self)
        return self._repository

    _serializer = None

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.real_name(), self.schema, self)
        return self._serializer

    def _retrieve(self):
        skip = request.args.get('skip') or 0
        if isinstance(skip, str):
            skip = int(skip)

        limit = request.args.get('limit') or None
        if isinstance(limit, str):
            limit = int(limit)

        query = parsers.RequestQueryParser.query_as_object()

        return query and self.repository.where(skip=skip, limit=limit, **query) \
            or self.repository.all(skip, limit)

    def _identify(self, entries):
        identity = commons.SchemaNavigator.identity_from(self.schema)

        try:
            return [e[identity] for e in entries]

        except KeyError:
            raise errors.BadRequestError('UNIDENTIFIABLE')

    def _update(self, entries):
        entries, rejected = self.serializer.validate(entries)

        self.trigger('before_update', entries=entries)
        entries = self.repository.update(entries)
        self.trigger('after_update', entries=entries)

        entries, fields = self.serializer.project(entries)

        status = 207 if entries and rejected else 200 if entries else 400

        content = {}
        if entries:
            content['updated'] = entries
        if rejected:
            content['failed'] = rejected

        return self.response(content, status=status, wrap=False, projection=fields)

    def get(self):
        try:
            self.trigger('before_retrieve')
            d = self._retrieve()
            self.trigger('after_retrieve', entries=d)

            d, page = self.paginator.paginate(d)
            d, fields = self.serializer.project(d)

            return self.response(d, projection=fields, page=page)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def post(self):
        try:
            entries, _ = commons.CollectionHelper.transform(request.form)
            entries, rejected = self.serializer.validate(entries)

            self.trigger('before_create', entries=entries)
            entries = self.repository.create(entries)
            self.trigger('after_create', entries=entries)

            entries, fields = self.serializer.project(entries)

            status = 207 if entries and rejected else 200 if entries else 400

            content = {}
            if entries:
                content['created'] = entries
            if rejected:
                content['failed'] = rejected

            return self.response(content, status=status, wrap=False, projection=fields)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def put(self):
        try:
            entries, _ = commons.CollectionHelper.transform(request.form)
            # Makes sure every entry has an identity.
            self._identify(entries)

            return self._update(entries)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def patch(self):
        try:
            r, _ = commons.CollectionHelper.transform(request.form)

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
            if parsers.RequestQueryParser.query():
                # Parse query from request. These entities will be deleted.
                entries = self._retrieve()
            else:
                # No query was passed. Search for identities in the body.
                entries, _ = commons.CollectionHelper.transform(request.form)

            if not entries:
                raise errors.BadRequestError('DATA_CANNOT_BE_EMPTY')

            identities = self._identify(entries)
            del entries

            self.trigger('before_delete', identities=identities)
            entries = self.repository.delete(identities)
            self.trigger('after_delete', entries=entries)

            entries, fields = self.serializer.project(entries)

            return self.response({'deleted': entries}, projection=fields, wrap=False)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    @classmethod
    def describe(cls):
        description = super().describe()
        description.update(schema=cls.schema)

        return description


class EntityResource(SchematicResource):
    repository_class = repositories.GraphEntityRepository

    def __init__(self):
        super().__init__()

        assert issubclass(self.repository_class, repositories.base.EntityRepository)

    @classmethod
    def real_end_point(cls):
        """Retrieve the resource end-point based on its end-point or name.

        The end-point is chosen between one of the following, in desc order of priority:
            The :end_point class property, if set by the user;
            The :name class property, if set by the user;
            The plural form of the name of the class, if class property :pluralize is True;
            The name of the class.

        :return: :str: the string representing the end-point of the entity resource.
        """
        if cls.end_point is not None:
            end_point = cls.end_point
        else:
            end_point = cls.pluralize and commons.WordHelper.pluralize(cls.real_name()) or cls.real_name()

        end_point = '/'.join((settings.effective.BASE_END_POINT.lower(), end_point.lower())).replace('//', '/')

        return '/' + end_point if end_point[0] != '/' else end_point


class RelationshipResource(SchematicResource):
    origin = target = None
    cardinality = commons.Cardinality.many

    repository_class = repositories.GraphRelationshipRepository
    serializer_class = serializers.DynamicRelationshipSerializer

    def __init__(self):
        super().__init__()

        assert issubclass(self.repository_class, repositories.base.RelationshipRepository)

        if not self.origin or not self.target:
            raise ValueError('Relationship resources must have a valid origin and target attribute set.')

        # If one of the references are strings, import the actual classes.
        if isinstance(self.origin, str) or isinstance(self.target, str):
            user_resources = importlib.import_module('%s.%s' % (settings.effective.BASE_MODULE, 'resources'))

            if isinstance(self.origin, str):
                self.origin = getattr(user_resources, self.origin)
            if isinstance(self.target, str):
                self.target = getattr(user_resources, self.target)

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

    @classmethod
    def describe(cls):
        description = super().describe()
        description.update(
            description=cls.description or 'Relationship %s' % cls.real_name(),
            relationship={
                'origin': cls.origin.real_name(),
                'target': cls.target.real_name(),
                'cardinality': cls.cardinality
            }
        )

        return description
