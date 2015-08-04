from .base.models import Model


class Student(Model):
    fields = {'_id', 'username'}
    guarded = {'password'}
