from flask import views, jsonify
from .. import paginators
from .. import serializers, parsers, commons, settings, errors
from ..guardian import Guardian


class Resource(views.MethodView):
    name = None
    end_point = None
    description = None

    methods = ('GET', 'HEAD', 'OPTIONS', 'POST', 'PATCH', 'PUT', 'DELETE')

    @property
    def paginator(self):
        return paginators.Paginator

    @staticmethod
    def response(content=None, status=200, wrap=False, clean_content=True,
                 **meta):
        """Wraps the content with a default response structure and add metadata.

        :param content: the content that will be wrapped.
        :param status: the status to be sent with in the HTTP response.
        :param wrap: overrides content wrapping. If content is a :dict and
                     :meta != {}, :meta and :content are merged.
        :param clean_content: eliminate empty keys in content before adding it.
        :param meta: :dict that will be add to the '_metadata'
                     key in the response.

        :return: :tuple (:dict response , :int status)
        :raise ValueError: If the content is not a dictionary,
                           wrap was set to False and there's metadata to add.
        """
        result = {}

        if clean_content and content and isinstance(content, dict):
            content = {i: v for i, v in content.items() if v}

        if meta:
            result.update(meta)

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
                    # There's metadata to add, but the user didn't specified if
                    # the content to be wrapped. Since the content isn't
                    # a dictionary, merging isn't possible.
                    raise ValueError(
                            'Cannot merge %s into result dictionary. Please '
                            'define content as a dictionary or  set wrap to '
                            'True.' % str(content))

        return jsonify(result), status

    def real_name(self):
        """Retrieve the resource's real name based on the overwritten
        property :name or the class name.

        :return: :str: the name that clearly represents the resource.
        """
        return self.name or self.__class__.__name__

    def real_end_point(self):
        """Retrieve the resource end-point based on its end-point or name.

        :return: :str: the string representing the end-point of the resource.
        """
        end_point = (self.end_point
                     if self.end_point is not None
                     else self.real_name()).lower()
        end_point = '/'.join((settings.effective.BASE_END_POINT,
                              end_point)).replace('//', '/')

        return '/' + end_point if end_point[0] != '/' else end_point

    def describe(self):
        """Describe Resource.

        Notice that this method is often be overridden by sub-classes.

        :return: :dict that describes this resource.
        """
        return {
            'uri': self.real_end_point(),
            'description': self.description or 'Resource %s' % self.real_name(),
            'methods': self.methods,
        }

    def options(self):
        """Options HTTP method.

        Yields the same description as given by the method :describe.

        :return: :dict that represents the description of this resource.
        """
        return self.describe()


class SchematicResource(Resource):
    def __init__(self, schema):
        self.schema = schema
        self.serializer = serializers.DynamicSerializer(schema.model)

    @property
    def manager(self):
        return self.schema.manager

    def real_name(self):
        return self.name or self.schema.__name__

    def describe(self):
        description = super().describe()
        description.update(model=self.schema.model)

        return description

    def get(self):
        try:
            Guardian.check_permissions(self)

            query = parsers.QueryParser.parse()
            entries = self.manager.query_or_all(**query)

            entries, page = self.paginator.paginate(entries)
            entries, fields = self.serializer.project(entries)

            return self.response(entries, fields=fields, page=page, wrap=True)

        except errors.GrapherError as e:
            return self.response(status=e.status_code,
                                 errors=e.as_api_response())

    def post(self):
        try:
            Guardian.check_permissions(self)

            entries = parsers.DataParser.parse_or_raise()
            entries, rejected = self.serializer.validate(entries)

            entries, failed = self.manager.create(entries) if entries \
                else ({}, {})

            entries, fields = self.serializer.project(entries)

            status = 207 if entries and (rejected or failed) \
                else 200 if entries else 400

            return self.response({
                'created': entries,
                'rejected': rejected,
                'failed': failed
            }, status=status, fields=fields)

        except errors.GrapherError as e:
            return self.response(status=e.status_code,
                                 errors=e.as_api_response())

    def put(self):
        try:
            Guardian.check_permissions(self)

            entries = parsers.DataParser.parse_or_raise()
            entries, unidentified = self.manager.fetch(entries)

            return self._update(entries, unidentified)

        except errors.GrapherError as e:
            return self.response(status=e.status_code,
                                 errors=e.as_api_response())

    def patch(self):
        try:
            Guardian.check_permissions(self)

            request_entries = parsers.DataParser.parse_or_raise()
            database_entries, unidentified = self.manager.fetch(request_entries)

            # Patches the request data onto the database data.
            for i, entry in database_entries.items():
                entry.update(request_entries[i])

            del request_entries

            return self._update(database_entries, unidentified)

        except errors.GrapherError as e:
            return self.response(status=e.status_code,
                                 errors=e.as_api_response())

    def _update(self, entries, unidentified=None):
        entries, rejected = self.serializer.validate(entries)

        entries, failed = self.manager.update(entries) if entries else ({}, {})
        entries, fields = self.serializer.project(entries)

        status = 207 if entries and (rejected or failed or unidentified) \
            else 200 if entries else 400

        return self.response({
            'updated': entries,
            'failed': failed,
            'rejected': rejected,
            'unidentified': unidentified
        }, status=status, fields=fields)

    def delete(self):
        try:
            Guardian.check_permissions(self)

            query = parsers.QueryParser.parse_or_raise()
            entries = self.manager.query(**query)

            entries, failed = self.manager.delete(entries) \
                if entries \
                else ({}, {})
            entries, fields = self.serializer.project(entries)

            return self.response({
                'deleted': entries,
                'failed': failed
            }, fields=fields)

        except errors.GrapherError as e:
            return self.response(status=e.status_code,
                                 errors=e.as_api_response())


class EntityResource(SchematicResource):
    pluralize = settings.effective.PLURALIZE_ENTITIES_NAMES

    def real_end_point(self):
        """Retrieve the resource end-point based on its end-point or name.

        The end-point is chosen between one of the following, in desc order
        of priority:
            > The :end_point class property, if set by the user;
            > The :name class property, if set by the user;
            > The plural form of the name of the class, if class property
                :pluralize is True;
            > The name of the class.

        :return: :str: the string representing the end-point of the entity
            resource.
        """
        if self.end_point is not None:
            end_point = self.end_point
        else:
            end_point = self.pluralize and commons.WordHelper.pluralize(
                    self.real_name()) or self.real_name()

        end_point = '/'.join((settings.effective.BASE_END_POINT.lower(),
                              end_point.lower())).replace('//', '/')

        return '/' + end_point if end_point[0] != '/' else end_point


class RelationshipResource(SchematicResource):
    def describe(self):
        description = super().describe()
        description.update(description=self.description or 'Relationship %s'
                                                           % self.real_name(),
                           relationship={
                               'origin': self.schema.origin.real_name(),
                               'target': self.schema.target.real_name(),
                               'cardinality': self.schema.cardinality})

        return description
