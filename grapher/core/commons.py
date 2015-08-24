import abc
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

        return cls

    @classmethod
    def modify_identity_requirement(cls, schema, require=True):
        identity = cls.add_identity(schema).identity_from(schema)
        schema[identity]['required'] = require

        return cls


class Cardinality(metaclass=abc.ABCMeta):
    one = one_to_one = 1
    one_to_many = 2
    many_to_one = 3
    many = many_to_many = 4
