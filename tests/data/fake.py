from faker import Faker
from faker.providers import BaseProvider

from py2neo import Node

f = Faker()


class NodesProvider(BaseProvider):
    def node(self, p_args, p_kwargs,
             *args, **kwargs):
        if p_args:
            args = p_args
        if p_kwargs:
            kwargs = p_kwargs

        return Node(*args, **kwargs)

    def department(self, *args, **kwargs):
        return self.node(args, kwargs, 'Department', name=f.text(max_nb_chars=20))

    def program(self, *args, **kwargs):
        return self.node(args, kwargs, 'Program', title=f.text(max_nb_chars=20), level=f.random_int(1, 4))

    def user(self, *args, **kwargs):
        return self.node(args, kwargs, 'User', name=f.name(), email=f.email(), password=f.text(max_nb_chars=10))

    def course(self, *args, **kwargs):
        return self.node(args, kwargs, 'Course', title=f.text(max_nb_chars=10), credits=f.random_int(1, 6))

    def enrollment_cycle(self, *args, **kwargs):
        return self.node(args, kwargs, 'EnrollmentCycle',
                         year=f.year(), term=f.random_int(1, 4))


f.add_provider(NodesProvider)
