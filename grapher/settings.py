from .core.settings import BaseSettings


class DevelopmentSettings(BaseSettings):
    SECRET_KEY = '0A7AIJTUZ15QZFGQGLYRH04ZIEM1CIB9BLDH278UFWE7I5L001H4C9N8CQP7P55U'
    DEBUG = True

    DATABASES = {
        'default': {
            'uri': '127.0.0.1:7474/db/data/',
            'username': 'neo4j',
            'password': 'root',
        }
    }


class ProductionSettings(BaseSettings):
    SECRET_KEY = 'VGU4DKW8V0ED6CDRIR4J5DTND7EHYJPK8SHUDYJD7ZGXCVCZC8LDR71LBO4JKZWE'
    DEBUG = False
    TESTING = False


class TestingSettings(BaseSettings):
    SECRET_KEY = 'Q5TJ45E7POZ77E59UVMGHYW8FJ0SHQ38AXXNYMCKFUAMCMF38IDTN5I0KUCH2ISJ'
    TESTING = True


effective = DevelopmentSettings
