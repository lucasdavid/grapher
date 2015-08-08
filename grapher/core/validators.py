from cerberus import Validator


class GrapherValidator(Validator):
    def _validate_identity(self, identity, field, value):
        """Add "identity" property to schema.
        """

    def _validate_visible(self, identity, field, value):
        """Add "visible" property to schema.
        """

    def _validate_index(self, index, field, value):
        """Add "index" property to scheme.
        """
