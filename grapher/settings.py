import os


class BaseSettings(object):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = '#1?m3m+1d9#0md40$41!idm410nd18nJ1301j380n83n%1dn3&011*30'

    DEBUG = False
    TESTING = False

    DATABASES = {
        'default': {
            'uri': '127.0.0.1:7474/db/data/',
            'username': 'neo4j',
            'password': 'root',
        }
    }

    # Flags if partial recoveries should be attempted.
    # For instance, a list of entities to be created, where a single entity is not valid:
    #   Inserts all entities - except for the one that's not valid - and return two lists (created, failed), if True.
    #   Does not insert any of the entities, if False.
    ATTEMPT_PARTIAL_RECOVERIES = True


class DevelopmentSettings(BaseSettings):
    DEBUG = True


class ProductionSettings(BaseSettings):
    pass


class TestingSettings(BaseSettings):
    TESTING = True


current_settings = DevelopmentSettings
