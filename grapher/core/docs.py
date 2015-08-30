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
        return self.response({
            'title': settings.effective.DOCS['title'],
            'description': settings.effective.DOCS['description'],
            'resources': {r.real_name(): r.describe() for r in self.resources_to_describe},
        })
