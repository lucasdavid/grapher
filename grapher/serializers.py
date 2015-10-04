from flask_restful import request

from . import validators, errors


class Serializer:
    """Serializer for incoming and outgoing data by the resources.

    All data must be validated by a serializer before being sent to repositories.
    """

    def __init__(self, label, schema):
        self.label = label
        self.schema = schema

    _projected_fields = None

    @property
    def projected_fields(self):
        # Scan all fields that are tagged as "visible".
        self._projected_fields = self._projected_fields or \
                                 {f for f, d in self.schema.items() if 'visible' not in d or d['visible']}
        return self._projected_fields

    _validator = None

    @property
    def validator(self):
        self._validator = self._validator or validators.GrapherValidator(self.schema)
        return self._validator

    def validate(self, d):
        if not d:
            raise errors.BadRequestError(
                ('DATA_CANNOT_BE_EMPTY', (), ([{'hello': 'world'}],)),
            )

        accepted, rejected = {}, {}

        v = self.validator

        for i, e in enumerate(d):
            if v.validate(e):
                accepted[i] = e
            else:
                rejected[i] = v.errors

        return accepted, rejected

    def project(self, d):
        # For each entry, remove all (key->value) pair that isn't in the set
        # of projected fields, which are private or non-requested fields.
        for entry in d:
            for field in entry.keys() - self.projected_fields:
                del entry[field]

        return d, list(self.projected_fields)


class DynamicSerializer(Serializer):
    @property
    def projected_fields(self):
        """Overrides BaseSerializer :project_fields property to consider fields requested by the user.

        Usage:
            curl .../resource?fields=[field][,field]*
            curl localhost/user?fields=id,name
        """
        if self._projected_fields is None:
            fields = super().projected_fields

            if request.args.get('fields') is not None:
                # The user has requested a field projection onto the result.
                # Only get not empty fields, fixing requests errors such as "fields=,id,name" or "fields=id,name,"
                request_fields = {f for f in request.args.get('fields').split(',') if f}

                invalid_fields = request_fields - fields
                if invalid_fields:
                    # End-users have tried to project invalid fields, such
                    # as nonexistent fields or fields marked as not visible.
                    raise errors.BadRequestError(
                        ('INVALID_FIELDS', invalid_fields,
                         ('%s?fields=%s' % (request.base_url, ','.join(fields)),))
                    )

                self._projected_fields = fields & request_fields

        return self._projected_fields
