import abc


class It(object, metaclass=abc.ABCMeta):
    @classmethod
    def is_iterable(cls, variable):
        return '__iter__' in dir(variable)

    @classmethod
    def make_iterable(cls, variable):
        return [] if variable is None else \
            variable if cls.is_iterable(variable) else \
            [variable]

    @classmethod
    def unwrap(cls, variable, many=False):
        return variable[0] if many else variable


class DataCollector(object, metaclass=abc.ABCMeta):
    def __init__(self):
        self._data = None

    def load(self, data):
        self._data = data

        return self
