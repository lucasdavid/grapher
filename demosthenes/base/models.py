import abc


class Model(object, metaclass=abc.ABCMeta):
    fields = set()
    guarded = set()
