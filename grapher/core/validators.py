from . import filters
from .. import settings


class BaseValidation(filters.BaseFilter):
    def run(self, entities):
        """Run validation over a collection of :entities.

        :param entities: the entities over which the validation will run.
        :return: a tuple of accepted and declined entities.
        """
        accepted = entities
        declined = {}

        return accepted, declined


class BaseEntityValidation(BaseValidation):
    def run(self, entities):
        accepted = entities.keys()
        failed = {}

        for i, entity in entities.items():
            errors = self.clean(entity).validate(entity)

            if errors:
                accepted.remove(i)
                failed[i] = errors

        return accepted, failed

    def clean(self, entity):
        """Cleans entity, if required.

        :param entity: the entity to be clean.
        """
        return self

    def validate(self, entity):
        raise NotImplementedError


class EmptyEntityValidation(BaseEntityValidation):
    """Check if the entity is empty.
    """
    def validate(self, entity):
        errors = []

        if not entity:
            errors.append('Entity must have at least a single (key->value) pair.')

        return errors


class NotSupportedFields(BaseEntityValidation):
    """Check if entity contains any fields that are not in the :assignable-fields list.
    """
    _assignable_fields = None

    @property
    def assignable_fields(self):
        if self._assignable_fields is None:
            self._assignable_fields = {f for f, d in self.schema.items() if 'protect' not in d or not d['protect']}

        return self._assignable_fields

    def clean(self, entity):
        """Clean entity from not supported fields, if attempt-partial-recoveries is True.

        :param entity: the entity to be clean.
        """
        if settings.ATTEMPT_PARTIAL_RECOVERIES:
            not_supported = entity.keys() - self.assignable_fields

            for f in not_supported:
                del entity[f]

        return super().clean(entity)

    def validate(self, entity):
        errors = []

        not_supported = entity.keys() - self.assignable_fields
        if not_supported:
            errors.append('The fields %s are not supported.' % not_supported)

        return errors


class CorrectFieldTypes(BaseEntityValidation):
    def validate(self, entity):
        errors = []

        for field, value in entity.items():
            expected = self.schema[field]['type'].__name__
            actual = type(value).__class__.__name__

            if not isinstance(value, self.schema[field]['type']):
                errors.append('Expected %s to be %s. %s (%s) found.' % (field, expected, value, actual))

        return errors
