from flask import request, abort
from flask_restful import reqparse

from . import common, errors


class Serializer:
    dynamic_fields = True

    def __init__(self, schema, expose=(), protect=()):
        self.schema = schema
        self.fields = self.schema.keys()

        expose, protect = set(expose), set(protect)

        if expose and protect:
            # Prevents from defining expose and protect at the same time.
            # We don't want this, as the expected behavior becomes very obscure.
            raise errors.GrapherError('expose and protect Resource\'s fields cannot be defined at once.')

        nonexistent = (expose | protect) - self.fields - {'_id'}
        if nonexistent:
            raise errors.GrapherError('Fields {%s} were not declared in the schema.' % nonexistent)

        if expose:
            self.projected = expose
        elif protect:
            self.projected = self.fields - protect
        else:
            self.projected = self.fields

        request_fields = request.args.get('fields')
        if self.dynamic_fields and request_fields:
            request_fields = set(request_fields.split(','))

            invalid_fields = request_fields - self.projected
            if invalid_fields:
                # End-users have tried to project fields that are not listed as projectable,
                # such as protected or nonexistent fields. Motherfuckers.
                abort(400, 'Cannot project fields: %s.' % invalid_fields)

            self.projected = self.projected & request_fields

    _parser = None

    @property
    def parser(self):
        if not self._parser:
            self._parser = reqparse.RequestParser()

            for field in self.schema.keys() - {'_meta'}:
                self._parser.add_argument(field, **self.schema[field])

        return self._parser

    def digest(self):
        return self.parser.parse_args()

    def project(self, data):
        data, transformed = common.It.transform(data)

        for entry in data:
            for field in entry.keys() - self.projected:
                del entry[field]

        return common.It.restore(data, transformed), {'projected': list(self.projected)}


class GraphSerializer(Serializer):
    def project(self, data):
        return super().project([entry.properties for entry in data])
