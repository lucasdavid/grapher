import abc

from flask import Flask

from . import settings


class Environment(metaclass=abc.ABCMeta):
    instance = None

    def __init__(self, name):
        if self.instance is not None:
            raise RuntimeError('The environment %s is already running. '
                               'Only one instance is allowed.'
                               % Environment.instance.name)

        self.name = name
        self.settings = settings.effective

        self.app = Flask(name)
        self.app.config.from_object(self.settings)

        self.user_artifacts = {}
        self.schemas = {}

        Environment.instance = self
