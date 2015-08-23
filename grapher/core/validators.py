from cerberus import Validator


class GrapherValidator(Validator):
    def _validate_identity(self, identity, field, value):
        """Add "identity" property to schemas.
        """
        if not value:
            self._error(field, 'Cannot be %s because it represents the resource identity.' % (str(value)))

    def _validate_visible(self, visible, field, value):
        """Add "visible" property to schemas.
        """

    def _validate_index(self, index, field, value):
        """Add "index" property to schemas.
        """

    def _validate_relationship(self, relationship, field, value):
        """Add "relationship" property to schemas.
        """
