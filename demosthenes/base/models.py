import abc


class Model(object, metaclass=abc.ABCMeta):
    fields = None
    guarded = None
