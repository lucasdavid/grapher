import importlib

from flask_restful import request

from .base import Resource
from .. import managers
from ..managers import guardians
from .. import repositories, serializers, parsers, commons, settings, errors
from ..repositories import graph
from ..commons import CollectionHelper, RequestHelper


class SchematicResource(Resource):
    schema = {}

    manager_class = managers.Manager
    repository_class = repositories.base.Repository
    serializer_class = serializers.DynamicSerializer
    guardian_class = guardians.Guardian

    _manager = None
    _serializer = None
    _guardian = None

    @classmethod
    def initialize(cls):
        if not cls.initialized:
            super().initialize()

            if not cls.schema:
                cls.schema = {}

            commons.SchemaNavigator.add_identity(cls.schema)

    @property
    def manager(self):
        self._manager = self._manager or self.manager_class(self.real_name(), self.schema, self.repository_class)
        return self._manager

    @property
    def serializer(self):
        self._serializer = self._serializer or self.serializer_class(self.real_name(), self.schema)
        return self._serializer

    @property
    def guardian(self):
        self._guardian = self._guardian or guardians.Guardian(self.real_name())
        return self._guardian

    def get(self):
        try:
            self.guardian.check_permissions()

            self.em().trigger('before_retrieve')

            query = parsers.QueryParser.parse()
            entries = self.manager.query_or_all(**query)

            self.em().trigger('after_retrieve', entries=entries)

            entries, page = self.paginator.paginate(entries)
            entries, fields = self.serializer.project(entries)

            return self.response(d, fields=fields, page=page)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def post(self):
        try:
            self.guardian.check_permissions()

            entries = parsers.DataParser.parse_or_raise()
            entries, rejected = self.serializer.validate(entries)

            self.em().trigger('before_create', entries=entries, rejected=rejected)
            entries_values = self.manager.create(entries.values())
            entries = CollectionHelper.zip(entries.keys(), entries_values)

            self.em().trigger('after_create', entries=entries, rejected=rejected)

            entries_values, fields = self.serializer.project(entries.values())
            entries = CollectionHelper.zip(entries.keys(), entries_values)

            status = 207 if entries and rejected else 200 if entries else 400
            content = {}
            if entries:
                content['created'] = entries
            if rejected:
                content['failed'] = rejected

            return self.response(content, status=status, wrap=False, fields=fields)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def put(self):
        try:
            self.guardian.check_permissions()

            entries = DataParser.parse_or_raise()
            entries, unidentifiables = self._identify(entries)

            return self._update(entries.values())

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response(), wrap=False)

    def patch(self):
        try:
            self.guardian.check_permissions()

            r = parsers.DataParser.parse_or_raise()
            identifiables, unidentifiables = self._identify(r)

            identity = commons.SchemaNavigator.identity_from(self.schema)
            entries = self.manager.find([entity[identity] for entity in identifiables.values()])

            # Patches the request data onto the database data.
            for i, data in identifiables.items():
                entries[i].update(data)
            del r

            return self._update(entries, unidentifiables)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    def _identify(self, entities):
        identity = commons.SchemaNavigator.identity_from(self.schema)
        identifiables, unidentifiables = {}, {}

        for i, entity in enumerate(entities):
            if identity in entity:
                identifiables[i] = entity
            else:
                unidentifiables[i] = entity

        return identifiables, unidentifiables

    def _update(self, entries, unidentifiables=None):
        entries, rejected = self.serializer.validate(entries)

        self.em().trigger('before_update', entries=entries, rejected=rejected)

        entries_values = self.repository.update(entries.values())
        entries = CollectionHelper.zip(entries.keys(), entries_values)

        self.em().trigger('after_update', entries=entries, rejected=rejected)

        entries_values, fields = self.serializer.project(entries.values())
        entries = CollectionHelper.zip(entries.keys(), entries_values)

        status = 207 if entries and rejected else 200 if entries else 400
        content = {}
        if entries:
            content['updated'] = entries
        if rejected:
            content['failed'] = rejected
        if unidentifiables:
            content['unidentifiables'] = unidentifiables

        return self.response(content, status=status, wrap=False, fields=fields)

    def delete(self):
        try:
            self.guardian.check_permissions()

            self.em().trigger('before_delete', identifiables=identifiables)

            query = parsers.QueryParser.parse_or_raise()
            entries = self.manager.query(**query);
            entries, failed = self.manager.delete([e[self.identity] for e in entries])
            entries, fields = self.serializer.project(entries)

            self.em().trigger('after_delete', entries=entries)

            return self.response({'deleted': entries}, fields=fields, wrap=False)

        except errors.GrapherError as e:
            return self.response(status=e.status_code, errors=e.as_api_response())

    @classmethod
    def describe(cls):
        description = super().describe()
        description.update(schema=cls.schema)

        return description


class EntityResource(SchematicResource):
    pluralize = settings.effective.PLURALIZE_ENTITIES_NAMES
    repository_class = graph.GraphEntityRepository

    @classmethod
    def initialize(cls):
        if not cls.initialized:
            super().initialize()

            assert issubclass(cls.repository_class, repositories.base.EntityRepository)

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

    repository_class = graph.GraphRelationshipRepository

    @classmethod
    def initialize(cls):
        if not cls.initialized:
            super().initialize()

            assert issubclass(cls.repository_class, repositories.base.RelationshipRepository)

            if not cls.origin or not cls.target:
                raise ValueError('Relationship resources must have a valid origin and target attribute set.')

            # If one of the references are strings, import the actual classes.
            if isinstance(cls.origin, str) or isinstance(cls.target, str):
                user_resources = importlib.import_module('%s.%s' % (settings.effective.BASE_MODULE, 'resources'))

                if isinstance(cls.origin, str):
                    cls.origin = getattr(user_resources, cls.origin)
                if isinstance(cls.target, str):
                    cls.target = getattr(user_resources, cls.target)

            # Initialize origin and target resources, as we have to access their schemas.
            cls.origin.initialize()
            cls.target.initialize()

            # Make sure classes are :EntityResource sub-class, as they are databases' entities.
            if not issubclass(cls.origin, EntityResource):
                raise ValueError(
                    'Origin references {%s}. Try a EntityResource subclass instead.' % EntityResource.__name__)
            if not issubclass(cls.target, EntityResource):
                raise ValueError(
                    'Target references {%s}. Try a EntityResource subclass instead.' % EntityResource.__name__)

            # Check if cardinality has a valid value.
            if cls.cardinality not in commons.Cardinality.types:
                raise ValueError('Cardinality must be one of the following: %s. %s was given.' % (
                    str(commons.Cardinality.types), str(cls.cardinality)))

            # Injecting :_origin and :_target properties in schema.
            # They are fundamental as this is a relationship resource.
            identity = commons.SchemaNavigator.add_identity(cls.origin.schema)
            cls.schema['_origin'] = {
                'required': True,
                'type': cls.origin.schema[identity]['type'],
            }

            identity = commons.SchemaNavigator.add_identity(cls.target.schema)
            cls.schema['_target'] = {
                'required': True,
                'type': cls.target.schema[identity]['type'],
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
