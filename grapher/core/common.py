import abc


class It(metaclass=abc.ABCMeta):
    @classmethod
    def is_list(cls, entry_or_collection):
        return isinstance(entry_or_collection, (list, tuple, set))

    @classmethod
    def transform(cls, entry_or_collection):
        if entry_or_collection is None:
            return None, False

        return (entry_or_collection, False) if cls.is_list(entry_or_collection) \
            else ([entry_or_collection], True)

    @classmethod
    def restore(cls, entry_or_collection, was_previously_transformed=False):
        return entry_or_collection.pop() if was_previously_transformed else entry_or_collection


class DataCollector(metaclass=abc.ABCMeta):
    def __init__(self):
        self._data = None

    def load(self, data):
        self._data = data

        return self
