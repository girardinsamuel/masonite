import inspect
from .RuleEnclosure import RuleEnclosure
from .MessageBag import MessageBag
from .rules import ValidationFactory
from ..exceptions import ValidationException


class Validator:
    def __init__(self, data: dict, *rules, raise_exception=False) -> None:
        self.data = data
        self.rules = rules
        self.raise_exception = raise_exception

        self.error_bag = None

    # @M5: make raise_exception=True the default
    def validate(self) -> dict:
        rule_errors = {}
        try:
            # handle all rules
            for rule in self.rules:
                if isinstance(rule, str):
                    rule = self.parse_string(rule)
                    # continue
                elif isinstance(rule, dict):
                    rule = self.parse_dict(rule, self.data, rule_errors)
                    continue

                elif inspect.isclass(rule) and isinstance(rule(), RuleEnclosure):
                    rule_errors.update(self.run_enclosure(rule(), self.data))
                    continue

                rule.handle(self.data)
                for error, message in rule.errors.items():
                    if error not in rule_errors:
                        rule_errors.update({error: message})
                    else:
                        messages = rule_errors[error]
                        messages += message
                        rule_errors.update({error: messages})
                rule.reset()

            self.error_bag = MessageBag(rule_errors)
            if self.error_bag.any():
                if self.raise_exception:
                    raise ValidationException(self.error_bag)
            else:
                return self

        # an error occured during validation
        except Exception as e:
            e.errors = rule_errors
            raise e

    def validated(self) -> dict:
        return self.data

    def valid(self):
        return self.error_bag.empty()

    def invalid(self):
        return not self.valid()

    def parse_string(self, rule):
        rule, parameters = rule.split(":")[0], rule.split(":")[1].split(",")
        return ValidationFactory().registry[rule](parameters)

    def parse_dict(self, rule, dictionary, rule_errors):
        for value, rules in rule.items():
            for rule in rules.split("|"):
                rule, args = rule.split(":")[0], rule.split(":")[1:]
                rule = ValidationFactory().registry[rule](value, *args)

                rule.handle(dictionary)
                for error, message in rule.errors.items():
                    if error not in rule_errors:
                        rule_errors.update({error: message})
                    else:
                        messages = rule_errors[error]
                        messages += message
                        rule_errors.update({error: messages})

    def run_enclosure(self, enclosure, dictionary):
        rule_errors = {}
        for rule in enclosure.rules():
            rule.handle(dictionary)
            for error, message in rule.errors.items():
                if error not in rule_errors:
                    rule_errors.update({error: message})
                else:
                    messages = rule_errors[error]
                    messages += message
                    rule_errors.update({error: messages})
            rule.reset()
        return rule_errors
