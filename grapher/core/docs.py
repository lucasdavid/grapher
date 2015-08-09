from .resources import BaseResource


class Docs(BaseResource):
    end_point = '/'

    resources_to_describe = ()

    @classmethod
    def describe_all(cls):
        return {r.clean_name(): cls.describe(r) for r in cls.resources_to_describe}

    @classmethod
    def describe(cls, resource):
        return {
            'uri': resource.real_end_point(),
            'description': resource.description,
            'schema': resource.schema,
            'methods': resource.methods
        }

    def get(self):
        return self.response({
            'description': 'Grapher documentation',
            'resources': self.describe_all(),
        })
