class GrapherError(RuntimeError):
    pass


class SchemaError(GrapherError):
    pass


class SchemaDefinitionError(SchemaError):
    def __init__(self, message, *fields):
        super().__init__(message % fields)


class ConflictingIdentityError(SchemaDefinitionError):
    def __init__(self, field_a, field_b):
        super().__init__('The fields %s are both marked as identity of the resource.' % (field_a, field_b))


class ComponentInstantiationError(GrapherError):
    def __init__(self, component, *args):
        super().__init__('Cannot construct %s with the following arguments: %s' % (
            component.__class__.__name__, args))


class FactoryError(GrapherError):
    pass


