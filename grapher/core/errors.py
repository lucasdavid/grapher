from flask_restful import request, abort
from .. import settings


class GrapherError(RuntimeError):
    """Raised when it becomes clear that Grapher can no longer maintain the integrity of the current operation.

    A list of errors should be passed on instantiation. E.g.:
        ('INVALID_FIELDS', invalid_fields, fields)
        ('DATA_CANNOT_BE_EMPTY', data, [{'example': 10}])
    """
    status_code = 500

    def __init__(self, *errors):
        self.errors = errors

    def as_api_response(self):
        """Return a dictionary which represents a answer to the API user.

        :return: :dict: containing information about the errors raised.
        """
        errors = {}

        for code, description, suggestions in self.errors:
            error = settings.effective.ERRORS[code].copy()
            error['description'] %= list(description)
            error['suggestions'] = list(suggestions)

            errors[code] = error

        return errors


class BadRequestError(GrapherError):
    """Raised when it becomes clear the user has made a illicit request.
    """
    status_code = 400
