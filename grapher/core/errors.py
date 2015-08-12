from flask_restful import request, abort
from .. import settings


class GrapherError(RuntimeError):
    pass


class BadRequestError(GrapherError):
    """Usually instantiated when it becomes clear the user has made a illicit request.

    A list of errors should be passed on instantiation. E.g.:
        ('INVALID_FIELDS', invalid_fields, fields)
        ('DATA_CANNOT_BE_EMPTY', data, [{'example': 10}])

    Should be raised or instantiated, followed by :.abort() the call.

    """
    def __init__(self, *errors):
        self.errors = errors

    def as_api_response(self):
        """Return a dictionary which represents how bad is the request.


        :return: :dict: containing information about the errors raised.
        """
        response = {
            'uri': request.url,
            'errors': {},
        }

        for code, description, suggestions in self.errors:
            error = settings.effective.ERRORS[code].copy()
            error['description'] %= list(description)
            error['suggestions'] = list(suggestions)

            response['errors'][code] = error

        return response

    def abort(self, status_code=400):
        """Abort current API link, returning the data about the errors to the users.

        :param status_code: the status that will be sent to the peer. Notice that,
        as this class is called BadRequestError, you can only send 4** errors.
        """
        assert 400 <= status_code < 500
        abort(status_code, **self.as_api_response())
