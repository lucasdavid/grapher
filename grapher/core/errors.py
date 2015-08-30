from . import commons, settings


class GrapherError(RuntimeError):
    """Raised when it becomes clear that Grapher can no longer maintain the integrity of the current operation.

    GrapherError implements the :as_api_response() method, which returns a dictionary as
    (key)->(description, suggestions). If you wish to create custom errors, simply extend GrapherError and set the
    appropriate status_code.

    Errors should be passed on instantiation. E.g.:
        'DATA_CANNOT_BE_EMPTY',
        ('NOT_FOUND', 1),
        ('INVALID_FIELDS', invalid_fields, example_fields)
    """
    status_code = 500

    def __init__(self, *errors):
        self.errors = errors

    def as_api_response(self):
        """Return a dictionary which represents a answer to the API user.

        :return: :dict: containing information about the errors raised.
        """
        errors = {}

        if 500 <= self.status_code < 600:
            errors['INTERNAL_ERROR'] = settings.effective.ERRORS['INTERNAL_ERROR']

        else:
            for error in self.errors:
                error, _ = commons.CollectionHelper.transform(error)

                code = error[0]
                e = settings.effective.ERRORS[code].copy()

                if len(error) > 1:
                    e['description'] %= error[1]

                    if len(error) > 2:
                        e['suggestions'] = error[2]

                errors[code] = e

        return errors


class BadRequestError(GrapherError):
    """Raised when it becomes clear the user has made a illicit request.
    """
    status_code = 400


class NotFoundError(BadRequestError):
    status_code = 404
