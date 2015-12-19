import copy


class Schema:
    def __init__(self, **attributes):
        self._data = copy.deepcopy(attributes)

    def __getattr__(self, item):
        return self._data[item]

    def __setattr__(self, key, value):
        self._data[key] = value
        return value

    def __delattr__(self, item):
        del self._data[item]


class Entity(Schema):
    pass


class Relationship(Schema):
    origin = None
    target = None
