import os


class Settings:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    DEBUG = False
    TESTING = False

    BASE_URL = ''

    DATABASES = {}

    # Flags if partial recoveries should be attempted.
    # For instance, a list of entities to be created, where a single entity is not valid:
    #   Inserts all entities - except for the one that's not valid - and return two lists (created, failed), if True.
    #   Does not insert any of the entities, if False.
    ATTEMPT_PARTIAL_RECOVERIES = True

    DOCS = {
        'title': 'Grapher',
        'description': 'Welcome to Grapher!',
    }

    ERRORS = {
        'DATA_CANNOT_BE_EMPTY': {
            'description': 'The requested action needs some data to process.',
        },
        'INVALID_FIELDS': {
            'description': 'The requested fields %s are invalid.',
        },
        'NOT_FOUND': {
            'description': 'The entity %s was not found in the database.',
        },
        'UNIDENTIFIABLE': {
            'description': 'This operation requires all instances to have an identity.',
        }
    }
