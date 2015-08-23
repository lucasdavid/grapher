import abc


class Factory(metaclass=abc.ABCMeta):
    classes = ()
    suffix = ''

    def __init__(self):
        self.storage = {}

        for c in self.classes:
            tag = c.__name__.lower()

            self.storage[tag] = c

    def build(self, tag, *args, **kwargs):
        tag = tag.lower()

        if tag in self.storage:
            c = self.storage[tag]

