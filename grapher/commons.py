import abc
import flask_restful
from cerberus import SchemaError


class CollectionHelper(metaclass=abc.ABCMeta):
    """Helper for normalizing unknown structures into lists.
    """

    @classmethod
    def needs(cls, item):
        """Checks if :item needs to be transformed into a list.

        Fundamentally, lists, tuples, sets and objects that have a member '__iter__' don't need transformation,
        except for dictionaries and objects of their subclasses.

        :param item: the unknown structure.
        :return: :boolean:
        """
        return not isinstance(item, (list, tuple, set)) and \
               not hasattr(item, '__iter__') or isinstance(item, dict) or issubclass(item.__class__, dict) or \
               isinstance(item, str)

    @classmethod
    def transform(cls, item):
        """Transforms an unknown structure into a list, if it isn't one yet.

        :param item: the structure to be transformed.
        :return: a list containing the passed structure, or the structure itself, if it's already a list.
        """
        return ([item], True) if cls.needs(item) \
            else (item, False)

    @classmethod
    def restore(cls, item, previously_transformed):
        """Restore a structure to its original state.

        :param item: the structure to be restored.
        :param previously_transformed: the flag which indicates if the structure was previously transformed.
        :return: the structure, in case it was not transformed. The element in the first-level of the list, otherwise.
        """
        return item.pop() if previously_transformed else item

    @classmethod
    def enumerate(cls, item):
        item, transformed = cls.transform(item)
        item = {i: e for i, e in enumerate(item)}

        return item, transformed

    @classmethod
    def restore_enumeration(cls, item, previously_transformed):
        item = [e for _, e in item.items()]

        return cls.restore(item, previously_transformed)


class SchemaNavigator(metaclass=abc.ABCMeta):
    @classmethod
    def identity_from(cls, schema):
        # Let's assume :_id is the identity field.
        identity = None

        # Now, we override :_id, if explicitly flagged by the user.
        for field, desc in schema.items():
            if 'identity' in desc and desc['identity']:
                if identity:
                    raise SchemaError('Cannot define both fields %s and %s as identity.', identity, field)

                identity = field

        return identity or '_id'

    @classmethod
    def add_identity(cls, schema):
        identity = cls.identity_from(schema)

        if identity not in schema:
            # Don't do anything in case there's a identity already.
            schema[identity] = {'type': 'integer', 'identity': True}

        return identity


class Cardinality(metaclass=abc.ABCMeta):
    one = '1'
    one_to_many = '1-*'
    many_to_one = '*-1'
    many = '*'

    types = {one, one_to_many, many_to_one, many}


class WordHelper(metaclass=abc.ABCMeta):
    aberrant_plural_map = {
        'appendix': 'appendices',
        'barracks': 'barracks',
        'cactus': 'cacti',
        'child': 'children',
        'criterion': 'criteria',
        'deer': 'deer',
        'echo': 'echoes',
        'elf': 'elves',
        'embargo': 'embargoes',
        'focus': 'foci',
        'fungus': 'fungi',
        'goose': 'geese',
        'hero': 'heroes',
        'hoof': 'hooves',
        'index': 'indices',
        'knife': 'knives',
        'leaf': 'leaves',
        'life': 'lives',
        'man': 'men',
        'mouse': 'mice',
        'nucleus': 'nuclei',
        'person': 'people',
        'phenomenon': 'phenomena',
        'potato': 'potatoes',
        'self': 'selves',
        'syllabus': 'syllabi',
        'tomato': 'tomatoes',
        'torpedo': 'torpedoes',
        'veto': 'vetoes',
        'woman': 'women',
    }

    vowels = set('aeiou')

    @classmethod
    def pluralize(cls, singular):
        """Return plural form of given lowercase singular word (English only).

        Based on ActiveState recipe http://code.activestate.com/recipes/413172/
        """
        if not singular:
            return ''
        plural = cls.aberrant_plural_map.get(singular)
        if plural:
            return plural
        root = singular
        try:
            if singular[-1] == 'y' and singular[-2] not in cls.vowels:
                root = singular[:-1]
                suffix = 'ies'
            elif singular[-1] == 's':
                if singular[-2] in cls.vowels:
                    if singular[-3:] == 'ius':
                        root = singular[:-2]
                        suffix = 'i'
                    else:
                        root = singular[:-1]
                        suffix = 'ses'
                else:
                    suffix = 'es'
            elif singular[-2:] in ('ch', 'sh'):
                suffix = 'es'
            else:
                suffix = 's'
        except IndexError:
            suffix = 's'
        plural = root + suffix
        return plural
