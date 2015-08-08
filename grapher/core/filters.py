class BaseFilter:
    verbose_name = None

    def __init__(self, schema):
        self.schema = schema

    def run(self, item):
        raise NotImplementedError

    @classmethod
    def clean_name(cls):
        return cls.verbose_name or cls.__name__
