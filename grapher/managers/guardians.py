from flask_restful import request

from . import managers, settings


class Guardian(managers.Manager):
    def __init__(self, name, schema, repository_class):
        super().__init__(name, schema, repository_class)

    def check_permissions(self):
        # request.base_url
        return None
