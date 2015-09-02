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

        for resource_class in self.resources_to_describe:
            r = resource_class()
            d['resources'][r.real_name()] = r.describe()

        return self.response(d, wrap=False)
