from ...providers import Provider
from .. import ValidationFactory, Form
from ..Validation import Validation
from ..commands.MakeRuleEnclosureCommand import MakeRuleEnclosureCommand
from ..commands.MakeRuleCommand import MakeRuleCommand


class ValidationProvider(Provider):
    """Validation service provider to handle data validation."""

    def __init__(self, application):
        self.application = application

    def register(self):
        validation = Validation()
        self.application.bind("validator", validation)
        self.application.make("commands").add(
            MakeRuleEnclosureCommand(self.application),
            MakeRuleCommand(self.application),
        )

        validation.extend(ValidationFactory().registry)

    def boot(self):
        self.application.resolving(
            Form,
            lambda obj, app: obj.set_request(app.make("request")),
        )

        self.application.after_resolving(
            Form,
            lambda obj, app: obj.validate_when_resolved(),
        )
