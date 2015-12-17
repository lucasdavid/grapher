import abc
from flask_oauthlib.provider import OAuth2Provider
from passlib.apps import custom_app_context as pwd_context
# from flask_restful import request

from .. import settings
from ..managers.base import Manager

oauth = OAuth2Provider()


class Guardian:
    def __init__(self, resource):
        self.resource = resource

    def check_permissions(self):
        pass

    def hash(self, password):
        return pwd_context.encrypt(password)

    def verify(self, password, hashed_password):
        return pwd_context.verify(password, hashed_password)

    @oauth.clientgetter
    def load_client(self, client_id):
        return self.repository.find()

