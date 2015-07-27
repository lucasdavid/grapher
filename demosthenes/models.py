from .base.models import Model


class Student(Model):
    fields = {'id', 'name'}
    guarded = {'password'}
