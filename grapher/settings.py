import os


class BaseSettings:
    TITLE = 'Grapher'
    DESCRIPTION = ''

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = 'VMR5SN7G9APTR98B31QMMKRMZVR2J0CCHK5XYJJ91DMB3N2A0HIHFKMGE97MDBP2'

    DEBUG = False
    TESTING = False

    BASE_URL = ''

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

    DOCS = {}


class DevelopmentSettings(BaseSettings):
    SECRET_KEY = '0A7AIJTUZ15QZFGQGLYRH04ZIEM1CIB9BLDH278UFWE7I5L001H4C9N8CQP7P55U'
    DEBUG = True


class ProductionSettings(BaseSettings):
    SECRET_KEY = 'VGU4DKW8V0ED6CDRIR4J5DTND7EHYJPK8SHUDYJD7ZGXCVCZC8LDR71LBO4JKZWE'


class TestingSettings(BaseSettings):
    SECRET_KEY = 'Q5TJ45E7POZ77E59UVMGHYW8FJ0SHQ38AXXNYMCKFUAMCMF38IDTN5I0KUCH2ISJ'
    TESTING = True


effective = DevelopmentSettings
