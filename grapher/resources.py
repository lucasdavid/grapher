from .base import resources


class HomeResource(resources.BaseResource):
    uri = '/'

    def get(self):
        return 'Hello world!'


class StudentResource(resources.GraphModelResource):
    model = {
        'name': 'Student',
        'uri': '/students',
        'fields': {
            'public': {'_id', 'username'},
            'private': {'password'},
        },
    }
