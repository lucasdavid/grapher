import abc


class CollectionHelper(metaclass=abc.ABCMeta):
    """Helper for normalizing unknown structures into lists.
    """
    @classmethod
    def needs(cls, entry_or_collection):
        """Checks if :entry_or_collection needs to be transformed into a list.

        :param entry_or_collection: the unknown structure.
        :return: :boolean:
        """
        return not isinstance(entry_or_collection, (list, tuple, set))

    @classmethod
    def transform(cls, entry_or_collection):
        """Transforms an unknown structure into a list, if it needs to.

        :param entry_or_collection: the structure to be transformed.
        :return: a list containing the passed structure, or the structure itself, if it's already a list.
        """
        if entry_or_collection is None:
            return None, False

        return ([entry_or_collection], True) if cls.needs(entry_or_collection) \
            else (entry_or_collection, False)

    @classmethod
    def restore(cls, collection, was_previously_transformed):
        """Restore a structure to its original state.

        :param collection: the structure to be restored.
        :param was_previously_transformed: the flag which indicates if the structure was previously transformed.
        :return: the structure, in case it was not transformed. The element in the first-level of the list, otherwise.
        """
        return collection.pop() if was_previously_transformed else collection
