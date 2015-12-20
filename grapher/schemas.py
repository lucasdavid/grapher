import abc
from . import commons, events


class Schema(events.AppLifeCycleEventListener, metaclass=abc.ABCMeta):
    manager = None
    repository = None
    serializer = None
    resource = None
    model = None

    class Meta:
        type = 'base'

    def __init__(self, **attributes):
        self._data = attributes

    def __getattr__(self, item):
        return self._data[item]

    def __setattr__(self, key, value):
        self._data[key] = value
        return value

    def __delattr__(self, item):
        del self._data[item]

    @classmethod
    def on_app_start(cls):
        if cls.model is None:
            cls.model = {}

        cls.Meta.identity = commons.SchemaNavigator.add_identity(cls.model)

        # if not cls.origin or not cls.target:
        #     raise ValueError('Relationship resources must have a valid '
        #                      'origin and target attribute set.')
        #
        # # If one of the references are strings, import the actual classes.
        # if isinstance(cls.origin, str) or isinstance(cls.target, str):
        #     user_resources = importlib.import_module(
        #             '%s.%s' % (settings.effective.BASE_MODULE, 'resources'))
        #
        #     if isinstance(cls.origin, str):
        #         cls.origin = getattr(user_resources, cls.origin)
        #     if isinstance(cls.target, str):
        #         cls.target = getattr(user_resources, cls.target)
        #
        # # Initialize origin and target resources
        # # in order to access their schemas.
        # if not cls.origin.initialized:
        #     cls.origin.initialize()
        # if not cls.target.initialized:
        #     cls.target.initialize()
        #
        # # Make sure origin and target are :EntityResource sub-class,
        # # as they are databases' entities.
        # if not issubclass(cls.origin, EntityResource):
        #     raise ValueError('Origin references {%s}.'
        #                      'Try a EntityResource subclass instead.'
        #                      % EntityResource.__name__)
        # if not issubclass(cls.target, EntityResource):
        #     raise ValueError('Target references {%s}.'
        #                      'Try a EntityResource subclass instead.'
        #                      % EntityResource.__name__)
        #
        # # Check if cardinality has a valid value.
        # if cls.cardinality not in commons.Cardinality.types:
        #     raise ValueError('Cardinality must be one of the following: %s.'
        #                      '%s was given.'
        #                      % (str(commons.Cardinality.types),
        #                         str(cls.cardinality)))
        #
        # # Injecting :_origin and :_target properties in schema.
        # # They are fundamental as this is a relationship resource.
        # identity = commons.SchemaNavigator.add_identity(cls.origin.schema)
        # cls.schema['_origin'] = {
        #     'required': True,
        #     'type': cls.origin.schema[identity]['type'],
        # }
        #
        # identity = commons.SchemaNavigator.add_identity(cls.target.schema)
        # cls.schema['_target'] = {
        #     'required': True,
        #     'type': cls.target.schema[identity]['type'],
        # }

    @classmethod
    def on_app_dispose(cls):
        del cls.view, cls.serializer, cls.manager, cls.repository

    @classmethod
    def on_app_end(cls):
        pass


class Entity(Schema, metaclass=abc.ABCMeta):
    class Meta:
        type = 'entity'


class Relationship(Schema, metaclass=abc.ABCMeta):
    origin = None
    target = None

    class Meta:
        type = 'relationship'
