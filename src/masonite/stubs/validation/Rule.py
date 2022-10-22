"""__class__ validation"""

from masonite.validation import BaseRule


class __class__(BaseRule):
    """__class__ validation class"""

    required_implied = False

    def passes(self, value, attribute: str, dictionary: dict) -> bool:
        """The passing criteria for this rule."""
        return True

    def message(self):
        """A message to show when this rule fails."""
        return "{attribute} is required"

    def negated_message(self):
        """A message to show when this rule is negated using a negation rule like 'isnt()'.

        For example if you have a message that says 'this is required' you may have a negated statement
        that says 'this is not required'."""
        return "{attribute} is not required"
