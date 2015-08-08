import abc


class CollectionHelper(metaclass=abc.ABCMeta):
    """Helper for normalizing unknown structures into lists.
    """

    @classmethod
    def needs(cls, item):
        """Checks if :item needs to be transformed into a list.

        :param item: the unknown structure.
        :return: :boolean:
        """
        return not isinstance(item, (list, tuple, set))

    @classmethod
    def transform(cls, item):
        """Transforms an unknown structure into a list, if it isn't one yet.

        :param item: the structure to be transformed.
        :return: a list containing the passed structure, or the structure itself, if it's already a list.
        """
        if item is None:
            return None, False

        return ([item], True) if cls.needs(item) \
            else (item, False)

    @classmethod
    def restore(cls, item, previously_transformed):
        """Restore a structure to its original state.

        :param item: the structure to be restored.
        :param previously_transformed: the flag which indicates if the structure was previously transformed.
        :return: the structure, in case it was not transformed. The element in the first-level of the list, otherwise.
        """
        return item.pop() if previously_transformed and item else item

    @classmethod
    def enumerate(cls, item):
        item, transformed = cls.transform(item)

        if item:
            item = {i: e for i, e in enumerate(item)}

        return item, transformed

    @classmethod
    def restore_enumeration(cls, item, previously_transformed):
        item = [e for _, e in item.items()]

        return item.pop() if previously_transformed and item else item
