import os


class Settings:
    BASE_MODULE = None
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = None

    DEBUG = False
    TESTING = False

    # A prefix of all end-points.
    BASE_END_POINT = ''

    # If True, EntityResources will try to pluralize their name
    # before exposing it. Notice that this behavior is overridden
    # by the :EntityResource.pluralize class property. Additionally,
    # pluralization will NOT happen if the user has set :EntityResource.name.
    PLURALIZE_ENTITIES_NAMES = True

    DATABASES = {
        'neo4j': {
            'uri': '127.0.0.1:7474/db/data/',
            'username': 'neo4j',
            'password': 'root'
        },
        'mongodb': {
            'name': 'default',
            'host': 'localhost',
            'port': 27017,
        }
    }

    AUTH = {
        'database': 'mongodb',
        'grant': {'expires_in_seconds': 100},
        'guardian_class': 'grapher.auth.guardians.Guardian'
    }

    # Flags if partial recoveries should be attempted.
    # For instance, a list of entities to be created, where a single entity
    # is not valid:
    #   Inserts all entities - except for the one that's not valid -
    #   and return two lists (created, failed), if True.
    #   Does not insert any of the entities, if False.
    ATTEMPT_PARTIAL_RECOVERIES = True

    DOCS = {
        'title': 'Grapher',
        'description': 'Welcome to Grapher!',
    }

    ERRORS = {
        'INTERNAL_ERROR': {
            'description': 'The server experienced some difficulties when'
                           'processing your request.',
        },
        'DATA_CANNOT_BE_EMPTY': {
            'description': 'The requested action needs some data to process.',
        },
        'INVALID_FIELDS': {
            'description': 'The requested fields %s are invalid.',
        },
        'NOT_FOUND': {
            'description': 'The entity %s was not found in the database.',
        },
        'INVALID_QUERY': {
            'description': 'The query is invalid: %s.',
        },
        'MISSING_QUERY': {
            'description': 'This operation requires a query, which was '
                           'not provided.',
        },
        'UNIDENTIFIABLE': {
            'description': 'This operation requires all instances to have '
                           'an identity.',
        },
        'CARDINALITY_1_MISMATCH': {
            'description': 'This relationship has cardinality 1 and does not '
                           'consume lists with many elements.',
        }
    }


class Development(Settings):
    DEBUG = True
    TESTING = True


class Production(Settings):
    DEBUG = False
    TESTING = False


class Testing(Settings):
    TESTING = True
    BASE_MODULE = 'tests.examples'


effective = Development
