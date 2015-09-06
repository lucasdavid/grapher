from . import resources, settings


class Docs(resources.Resource):
    """Docs resource, used for the API auto-documentation.

    This resource is registered automatically on Graph start-up.
    """

    end_point = '/'
    methods = ('GET',)

    # Dynamically filled during start-up.
    resources_to_describe = ()

    def get(self):
        d = {
            'title': settings.effective.DOCS['title'],
            'description': settings.effective.DOCS['description'],
            'resources': {},
        }

        for resource in self.resources_to_describe:
            resource.initialize()

            d['resources'][resource.real_name()] = resource.describe()

        return self.response(d, wrap=False)
