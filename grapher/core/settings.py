import os


class BaseSettings:
    TITLE = 'Grapher'
    DESCRIPTION = 'Welcome to Grapher!'

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    DEBUG = False
    TESTING = False

    BASE_URL = ''

    # Flags if partial recoveries should be attempted.
    # For instance, a list of entities to be created, where a single entity is not valid:
    #   Inserts all entities - except for the one that's not valid - and return two lists (created, failed), if True.
    #   Does not insert any of the entities, if False.
    ATTEMPT_PARTIAL_RECOVERIES = True

    DOCS = {}
