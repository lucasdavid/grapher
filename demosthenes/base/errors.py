class DemosthenesError(RuntimeError):
    pass


class ComponentInstantiationError(DemosthenesError):
    def __init__(self, component, *args):
        super().__init__('Cannot construct %s with the following arguments: %s' % (
            component.__class__.__name__, args))
