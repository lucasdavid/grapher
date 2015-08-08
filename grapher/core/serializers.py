from flask import request
from flask_restful import abort

from . import common, validators


class Serializer:
    dynamic_projection = True

    def __init__(self, schema, meta):
        self.schema = schema
        self.meta = meta

    _projected_fields = None

    @property
    def projected_fields(self):
        if self._projected_fields is None:
            # Scan all fields that are tagged as "visible".
            self._projected_fields = {f for f, d in self.schema.items() if 'visible' not in d or not d['visible']}

            if self.dynamic_projection and request.args.get('fields'):
                # Dynamic project is ON and the user has requested a field projection onto the result.
                request_fields = set(request.args.get('fields').split(','))

                invalid_fields = request_fields - self._projected_fields
                if invalid_fields:
                    # End-users have tried to project invalid fields, such
                    # as nonexistent fields or fields marked as not visible.
                    abort(400, errors=['Cannot project fields: %s. Make sure these fields do exist, that they are'
                                       ' marked as "visible" and you have permission to access them.' % invalid_fields])

                self._projected_fields = self._projected_fields & request_fields

        return self._projected_fields

    _v = None

    @property
    def v(self):
        self._v = self._v or validators.GrapherValidator(self.schema)
        return self._v

    def validate_or_abort_if_empty(self, d):
        if not d:
            abort(400, errors='Cannot validate empty data.')

        return self.validate(d)

    def validate(self, d):
        d, _ = common.CollectionHelper.transform(d)

        accepted = []
        declined = {}
    
        for i, e in enumerate(d):
            if self.v.validate(e):
                accepted.append(e)
            else:
                declined[i] = self.v.errors

        return accepted, declined

    def project(self, d):
        d, transformed = common.CollectionHelper.transform(d)

        # For each entry, remove all (key->value) pair that isn't in the set
        # of projected fields, which are private or non-requested fields.
        for entry in d:
            for field in entry.keys() - self.projected_fields:
                del entry[field]

        return common.CollectionHelper.restore(d, transformed), list(self.projected_fields)


class GraphSerializer(Serializer):
    def project(self, d):
        return super().project([entry.properties for entry in d])
