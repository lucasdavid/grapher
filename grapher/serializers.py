from flask_restful import request

from . import validators, errors


class Serializer:
    """Serializer for incoming and outgoing data by the resources.

    All data must be validated by a serializer before being sent
    to repositories.
    """

    def __init__(self, model):
        self.model = model

    _projected_fields = None

    @property
    def projected_fields(self):
        # Scan all fields that are tagged as "visible".
        self._projected_fields = self._projected_fields or \
                                 {f for f, d in self.model.items()
                                  if 'visible' not in d or d['visible']}
        return self._projected_fields

    _validator = None

    @property
    def validator(self):
        self._validator = (self._validator or
                           validators.GrapherValidator(self.model))
        return self._validator

    def validate(self, entries):
        """Validate entries according to a schema.

        :param entries: :dict: containing entries to be validated.
            E.g.: {0: {...}, 1: {...}, 2: {...}}.

        :return: :tuple: of :dict:, containing the entries that were
        accepted and rejected, respectively. E.g.:
            {0: {...}, 2: {...}}, {1: {...}}
        """
        accepted, rejected = {}, {}
        v = self.validator

        for i, entry in entries.items():
            if v.validate(entry):
                accepted[i] = entry
            else:
                rejected[i] = v.errors

        return accepted, rejected

    def project(self, entries):
        """For each entry in entries, remove all (key, value) pairs that
        are not in the set of projected fields, which are likely private
        or non-requested fields.

        This happens inplace: as this will be the last operation and the
        filtered info. will unlikely be reused, there is no need for building
        other dictionaries.

        :param entries: :dict: containing entries to be projected.
        E.g.: {0: {...}, 1: {...}, 2: {...}}.

        :return: :entries filtered.
        """
        for i, entry in entries.items():
            for field in entry.keys() - self.projected_fields:
                del entry[field]

        return entries, list(self.projected_fields)


class DynamicSerializer(Serializer):
    @property
    def projected_fields(self):
        """Overrides BaseSerializer :project_fields property to consider fields
        requested by the user.

        Usage:
            curl .../resource?fields=[field][,field]*
            curl localhost/user?fields=id,name
        """
        if self._projected_fields is None:
            fields = super().projected_fields

            if request.args.get('fields') is not None:
                # The user has requested a field projection onto the result.
                # Only get not empty fields, fixing requests errors such
                # as "fields=,id,name" or "fields=id,name,"
                request_fields = request.args.get('fields').split(',')
                request_fields = {f for f in request_fields if f}

                invalid_fields = request_fields - fields
                if invalid_fields:
                    # End-users have tried to project invalid fields, such
                    # as nonexistent fields or fields marked as not visible.
                    raise errors.BadRequestError(
                            ('INVALID_FIELDS', invalid_fields,
                             ('%s?fields=%s' % (
                             request.base_url, ','.join(fields)),))
                    )

                self._projected_fields = fields & request_fields

        return self._projected_fields
