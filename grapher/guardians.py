import abc


class Guardian(metaclass=abc.ABCMeta):
    resource = None

    def protect(self):
        raise NotImplementedError
