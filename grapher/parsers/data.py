import abc
from flask_restful import request

from .base import Parser
from .. import errors, commons


class DataParser(Parser, metaclass=abc.ABCMeta):
    @classmethod
    def parse(cls):
        d, _ = commons.CollectionHelper.enumerate(request.get_json())

        return d

    @classmethod
    def parse_or_raise(cls):
        d = cls.parse()

        if not d:
            raise errors.BadRequestError('DATA_CANNOT_BE_EMPTY')

        return d
