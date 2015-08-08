from flask import request
from flask_restful import abort

from . import common


class Serializer:
    dynamic_projection = True

    _projected_fields = None

    def __init__(self, schema, validators=()):
        self.schema = schema
        self.validators = validators

    @property
    def projected_fields(self):
        if self._projected_fields is None:
            self._projected_fields = {field for field, desc in self.schema.items() if
                                      'visible' not in desc or not desc['visible']}

            if self.dynamic_projection and request.args.get('fields'):
                # Dynamic project is ON and the user has requested a field projection onto the result.
                # We have to validate and filter the desired fields.
                request_fields = set(request.args.get('fields').split(','))

                invalid_fields = request_fields - self._projected_fields
                if invalid_fields:
                    # End-users have tried to project invalid fields, such
                    # as nonexistent fields or fields marked as not visible.
                    abort(400, message='Cannot project fields: %s. Make sure these fields do exist, that they are'
                                       ' marked as "visible" and you have permission to access them.' % invalid_fields)

                self._projected_fields = self._projected_fields & request_fields

        return self._projected_fields

    def validate(self, entries):
        entries = {i: e for i, e in enumerate(entries)}

        accepted = entries.keys()
        failed = {}

        for validator in self.validators:
            validator = validator(self.schema)

            a, f = validator.run(entries)

            # Filter entities accepted.
            accepted &= a

            # Register which errors have happened.
            for e, errors in f.items():
                if e not in failed:
                    failed[e] = {}

                failed[e][validator.clean_name()] = errors

        # Rescue entities associated with the accepted #ith.
        accepted = {i:e for i,e in entries.items() if i in accepted} if accepted else {}

        return accepted, failed

    def digest(self, data):
        accepted, declined = {}, {}

        data, _ = common.CollectionHelper.transform(data)
        if data:
            accepted, declined = self.validate(data)

        return accepted, declined

    def project(self, data):
        data, transformed = common.CollectionHelper.transform(data)

        # For each entry, remove all (key->value) pair that isn't in the set
        # of projected fields, which are private or non-requested fields.
        for entry in data:
            for field in entry.keys() - self.projected_fields:
                del entry[field]

        return common.CollectionHelper.restore(data, transformed), list(self.projected_fields)


class GraphSerializer(Serializer):
    def project(self, data):
        return super().project([entry.properties for entry in data])
