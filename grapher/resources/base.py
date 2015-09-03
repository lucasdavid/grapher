import flask_restful
from flask import request

from .. import settings, paginators


class Resource(flask_restful.Resource):
    """Grapher's base resource.

    Sub-classes of this declared in {settings.effective.BASE_MODULE}.resources
    module are automatically loaded as resources.
    """
    end_point = name = description = None
    pluralize = settings.effective.PLURALIZE_ENTITIES_NAMES

    methods = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT', 'DELETE')

    _paginator = None

    @classmethod
    def json(cls):
        """Wrap :request.json

        Used for testing, as we don't have access to requests in a unit-test environment.
        Additionally, might be overridden by sub-classes in order to pre-process input data
        before handling it to serializers.

        :return: :list or :dict which represents json data from the current request.
        """
        return request.json

    @property
    def paginator(self):
        self._paginator = self._paginator or paginators.Paginator()
        return self._paginator

    @classmethod
    def real_name(cls):
        """Retrieve the resource's real name based on the overwritten property :name or the class name.

        :return: :str: the name that clearly represents the resource.
        """
        return cls.name or cls.__name__

    @classmethod
    def real_end_point(cls):
        """Retrieve the resource end-point based on its end-point or name.

        :return: :str: the string representing the end-point of the resource.
        """
        end_point = (cls.end_point if cls.end_point is not None else cls.real_name()).lower()
        end_point = '/'.join((settings.effective.BASE_END_POINT, end_point)).replace('//', '/')

        return '/' + end_point if end_point[0] != '/' else end_point

    @classmethod
    def describe(cls):
        """Describe Resource.

        Notice that this method is often be overridden by sub-classes.

        :return: :dict that describes this resource.
        """
        return {
            'uri': cls.real_end_point(),
            'description': cls.description or 'Resource %s' % cls.real_name(),
            'methods': cls.methods,
        }

    @staticmethod
    def response(content=None, status=200, wrap=True, **meta):
        """Wraps the content with a default response structure and add metadata.

        :param content: the content that will be wrapped.
        :param status: the status to be sent with in the HTTP response.
        :param wrap: overrides content wrapping. If content is a :dict and :meta != {}, :meta and :content are merged.
        :param meta: :dict that will be add to the '_metadata' key in the response.

        :return: :tuple (:dict response , :int status)
        :raise ValueError: If the content is not a dictionary, wrap was set to False and there's metadata to add.
        """
        result = {}

        if meta:
            result['_meta'] = meta

        if content is not None:
            if wrap:
                result['content'] = content
            else:
                if isinstance(content, dict):
                    result.update(content)
                elif not meta:
                    # No metadata to add, content is the very whole response.
                    result = content
                else:
                    # There's metadata to add, but the user didn't specified if the content to be wrapped.
                    # Since the content isn't a dictionary, merging isn't possible.
                    raise ValueError(
                        'Cannot merge %s into result dictionary. Please define '
                        'content as a dictionary or set wrap to True.' % str(content))

        return result, status

    def _trigger(self, event, *args, **kwargs):
        """Triggers a specific event, in case it has been defined.

        :param event: the event to be triggered.
        :param args: positional arguments passed to the event.
        :param kwargs: key arguments passed to the event.
        :return: the event's result, in case it has been defined.
        """
        if hasattr(self, event):
            method = getattr(self, event)
            if method:
                return method(*args, **kwargs)

    def options(self):
        """Options HTTP method.

        Yields the same description as given by the method :describe.

        :return: :dict that represents the description of this resource.
        """
        return self.describe()
