import abc


class Parser(metaclass=abc.ABCMeta):
    """Parser base class.

    Parsers should implement both parse and parse_or_raise methods.
    """
    @classmethod
    def parse(cls):
        raise NotImplementedError

    @classmethod
    def parse_or_raise(cls):
        raise NotImplementedError
