from . import commons
from .commons import Debug
from .environment import Environment
from .managers import Manager
from .repositories import Repository
from .schemas import Schema
from .resources import Resource


class Grapher(Environment):
    instance = None

    components = [
        ('schemas', 'schema', Schema),
        ('repositories', 'repository', Repository),
        ('managers', 'manager', Manager),
        ('resources', 'resource', Resource),
    ]

    def __init__(self, name='Grapher'):
        super().__init__(name)

        for name, _, module in self.components:
            self.collect_user_artifacts(name, module)

        for name, schema in self.user_artifacts['schemas'].items():
            self.initialize(name, schema)

        self.register_resources()

        Grapher.instance = self

    def collect_user_artifacts(self, component, super_class):
        Debug.info('Collecting user\'s %s...' % component, end=' ')

        if self.settings.BASE_MODULE is None:
            raise ValueError('effective.BASE_MODULE is not set.')

        try:
            self.user_artifacts[component] = {}

            for name, c in commons.load_classes_in(
                    [self.settings.BASE_MODULE, component],
                    sub_classes_of=super_class):
                self.user_artifacts[component][name] = c

            Debug.message('Done.')

        except ImportError:
            Debug.message('Failed.')

        return self

    def initialize(self, name, schema):
        Debug.info('Initializing %s schema...' % name, end=' ')

        schema.on_app_start()
        user_schemas_module = '.'.join((self.settings.BASE_MODULE, 'schemas'))

        # Find components or instantiate the default ones.
        ua = self.user_artifacts

        for c_name, schema_attr, _ in [c for c in self.components if
                                       c[0] != 'schemas']:

            # Get component specified by user or default.
            if name in ua[c_name]:
                c = ua[c_name][name]
            else:
                c = self.settings.DEFAULT_COMPONENTS[schema.Meta.type][c_name]

            # If c is a string, resolve reference.
            c = commons.load_class(c, base_module=user_schemas_module)

            # Instantiates and add component to schema.
            setattr(schema, schema_attr, c(schema))

        self.schemas[name] = schema

        Debug.message('Done.')

    def register_resources(self):
        user_resources = set(self.user_artifacts['resources'])

        for name, schema in self.schemas.items():
            r = schema.resource
            end_point = r.real_end_point()

            Debug.info('Registering end-point %s...' % end_point, end=' ')

            if r.__class__ in user_resources:
                user_resources.remove(r.__class__)

            view_func = r.as_view('%s_schema_api' % name)
            self.app.add_url_rule(end_point, view_func=view_func)
            Debug.message('Done.')

        if user_resources:
            raise UserWarning('The following resources were declared by '
                              'are not being used: %s. Check nomenclature.'
                              % str(user_resources))
