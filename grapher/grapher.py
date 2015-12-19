from . import commons
from .commons import Debug
from .environment import Environment
from .managers import Manager
from .repositories import Repository
from .schemas import Schema
from .views import View


class Grapher(Environment):
    instance = None

    components = [
        ('schemas', 'schema', Schema),
        ('views', 'view', View),
        ('managers', 'manager', Manager),
        ('repositories', 'repository', Repository),
    ]

    def __init__(self, name='Grapher'):
        super().__init__(name)

        for name, _, module in self.components:
            self.collect_user_artifacts(name, module)

        for name, schema in self.user_artifacts['schemas'].items():
            self.initialize(name, schema)

        Grapher.instance = self

    def collect_user_artifacts(self, component, super_class):
        Debug.info('Collecting user\'s %s...' % component)

        if self.settings.BASE_MODULE is None:
            raise ValueError('effective.BASE_MODULE is not set.')

        try:
            self.user_artifacts[component] = {}

            for name, c in commons.load_classes_in(
                    [self.settings.BASE_MODULE, component],
                    sub_classes_of=super_class):
                self.user_artifacts[component][name] = c

            Debug.info('Done.')

        except ImportError:
            Debug.error('Failed.')

        return self

    def initialize(self, name, schema):
        Debug.info('Initializing %s schema...' % name)

        schema.initialize()

        user_schemas = '.'.join((self.settings.BASE_MODULE, 'schemas'))

        # Find components or instantiate the default ones.
        ua = self.user_artifacts

        for c_name, schema_attr, _ in [c for c in self.components if
                                       c[0] != 'schemas']:
            # Get component specified by user or default.
            c = ua[c_name][name] \
                if name in ua[c_name] \
                else self.settings.DEFAULT_COMPONENTS[c_name]

            # If c is a string, resolve reference.
            c = commons.load_class(c, base_module=user_schemas)

            # Instantiates and add component to schema.
            setattr(schema, schema_attr, c(schema))

        self.schemas[name] = schema

        Debug.info('Done.')
