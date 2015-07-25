from faker import Faker
from faker.providers import BaseProvider

from demosthenes import models as m

fake_data = Faker()


class DemosthenesModelProvider(BaseProvider):
    def student(self, **kwargs):
        kwargs.setdefault('name', fake_data.name())
        kwargs.setdefault('email', fake_data.email())

        return m.Student(**kwargs)


fake_data.add_provider(DemosthenesModelProvider)
