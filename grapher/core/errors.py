class GrapherError(RuntimeError):
    pass


class ComponentInstantiationError(GrapherError):
    def __init__(self, component, *args):
        super().__init__('Cannot construct %s with the following arguments: %s' % (
            component.__class__.__name__, args))


class FactoryError(GrapherError):
    pass
