import flask

from .common import It, DataCollector


class Serializer(DataCollector):
    project_from_url = True

    def __init__(self, model, request=None):
        super().__init__()

        self._model = model
        self._request = request or flask.request

    def get_fields(self):
        fields = self.project_from_url and flask.request.args.get('fields') or self._model.fields

        if isinstance(fields, str):
            # Fields come as a string from the request. Let's assume the user wrote
            # the fields that they wanted, separated by a comma.
            fields = fields.split(',')

        return set(fields)

    def get_public_fields(self):
        return self.get_fields() - set(self._model.guarded)

    def _detach_content_from_page(self):
        return self._data['content'] if 'content' in self._data else self._data

    def _reattach_content_to_page(self, content):
        if 'content' in self._data:
            self._data['content'] = content
        else:
            self._data = content

        return self._data

    def serialize(self):
        """Serialize the data according with the list of serializer.fields.

        :return: the serialized dict or dict list.
        """
        content = self._detach_content_from_page()

        if not content:
            # No content -> nothing to serialize.
            return self._data

        many = It.is_iterable(content)
        content = It.make_iterable(content)
        content = self._serialize(self.get_public_fields(), content)
        content = content if many else content[0]

        return self._reattach_content_to_page(content)

    def _serialize(self, fields, content):
        return [{f: e[f] for f in e.keys() & fields} for e in content]


class GraphSerializer(Serializer):
    def _serialize(self, fields, content):
        result = []

        for node in content:
            instance = {f: node.properties[f] for f in fields if f in node.properties}

            if '_id' in fields:
                instance['_id'] = node._id

            result.append(instance)

        return result
