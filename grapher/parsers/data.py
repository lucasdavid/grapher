from flask_restful import request

from .base import Parser
from ..commons import CollectionHelper


class DataParser(Parser, metaclass=abc.ABCMeta):
    @classmethod
    def parse(cls):
        d, _ = CollectionHelper.transform(request.get_json())

        return d

    @classmethod
    def parse_or_raise(cls):
        d = cls.get_data()

        if not d:
            raise errors.BadRequestError('DATA_CANNOT_BE_EMPTY')

        return d
