from . import resources
from .. import settings


class Docs(resources.Resource):
    """Docs resource, used for the API's auto-documenting feature.
    """

    end_point = '/'
    methods = ('GET',)

    # Dynamically filled during start-up.
    resources_to_describe = ()

    @classmethod
    def describe_all(cls):
        """Retrieve description of all resources declared in :resources_to_describe.

        :return: a set with pairs (resource-name->description).
        """
        return {r.clean_name(): cls.describe(r) for r in cls.resources_to_describe}

    @classmethod
    def describe(cls, resource):
        """Retrieve description of a given :resource.

        :param resource: the :BaseResource subclass that will be described.
        :return: the description generated.
        """
        return {
            'uri': resource.real_end_point(),
            'description': resource.description,
            'schema': resource.schema,
            'methods': resource.methods
        }

    def get(self):
        return self.response({
            'resources': self.describe_all(),
            'title': settings.effective.TITLE,
            'description': settings.effective.DESCRIPTION,
        })
