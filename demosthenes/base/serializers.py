import abc
import flask

from .common import It


class Serializer(object, metaclass=abc.ABCMeta):
    def __init__(self, data, fields=None, request=None):
        request = request or flask.request

        fields = flask.request.args.get('fields') or fields
        if isinstance(fields, str):
            # Fields come as a string from the request. Let's assume the user wrote
            # the fields that they wanted, separated by a comma.
            fields = fields.split(',')

        self._data = data
        self._request = request
        self._fields = fields

    def serialize(self):
        """Serialize the data according with the list of serializer.fields.

        :return: the serialized dict or dict list.
        """
        if not self._data:
            return self._data

        many = It.is_iterable(self._data)
        data = It.make_iterable(self._data)

        r = [{f: entry[f] for f in entry & set(self._fields)} for entry in data]

        return r if many else r[0]
