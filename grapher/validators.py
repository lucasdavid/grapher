from cerberus import Validator


class GrapherValidator(Validator):
    def _validate_identity(self, identity, field, value):
        """Add "identity" property to schemas.
        """

    def _validate_visible(self, visible, field, value):
        """Add "visible" property to schemas.
        """

    def _validate_index(self, index, field, value):
        """Add "index" property to schemas.
        """
