from typing import Any, List
from .RuleEnclosure import RuleEnclosure
from .MessageBag import MessageBag
from .rules import ValidationFactory
from .BaseRule import BaseRule
from ..utils.structures import data as convert_data


class Validator:
    implicit_rules = ["present", "filled", "required", "required_if", "required_with"]

    def __init__(
        self, data: dict, *dictionary_rules, validation_messages={}, placeholders={}
    ) -> None:
        self.data = convert_data(data)
        self.parent_attributes = {}
        all_rules_dict = {}
        for rules_dict in dictionary_rules:
            if isinstance(rules_dict, dict):
                all_rules_dict = {**all_rules_dict, **rules_dict}
            elif issubclass(rules_dict, RuleEnclosure):
                all_rules_dict = {**all_rules_dict, **rules_dict().rules()}
            else:
                raise Exception(
                    f"Validator rules can be RuleEnclosure or dict not {rules_dict}"
                )
        self.rules = self.explode_rules(all_rules_dict)
        self.raise_exception = True
        self.validation_messages = validation_messages
        self.placeholders = placeholders

        # to be filled when validating
        self.messages = MessageBag(dict())
        self.failed_rules = convert_data(dict())

        # # when logic
        # self._when_rules = {}
        # self._then_rules = {}

    def __repr__(self) -> str:
        return str(self.rules)

    def explode_rules(self, raw_rules):
        """Expand any "*" rules to the all of the explicit rules needed for the given data.
        For example the rule names.* would get expanded to names.0, names.1, etc. for this data"""
        rules = {}
        for attribute, attr_rules in raw_rules.items():
            # explode rules
            if "*" in attribute:
                array_of_values = self.get_value(attribute)
                parsed_rules = self.parse_rules(attr_rules)
                for index, value in enumerate(array_of_values):
                    nested_attribute = attribute.replace("*", str(index))
                    # TODO: merge instead ?
                    self.parent_attributes.update({nested_attribute: attribute})
                    rules[nested_attribute] = parsed_rules
            else:
                # TODO: merge instead ?
                rules[attribute] = self.parse_rules(attr_rules)

        return rules

    def validate(self):

        # check if when has been used
        # for attribute, when_rules in self._when_rules.items():
        #     value = self.get_value(attribute)
        #     if self.should_be_validated(attribute, rule, value):
        #         if not rule.passes(value, attribute, self.data):
        #             break

        #     if self.should_stop_validating(attribute):
        #         break

        #     # when validations are valid add then rules
        #     for attribute, then_rules in self._then_rules.items():
        #         self.rules[attribute] += self.then_rules[attribute]

        # run explicit rules
        for attribute, rules in self.rules.items():
            for rule in rules:
                value = self.get_value(attribute)
                if self.should_be_validated(attribute, rule, value):
                    if not rule.passes(value, attribute, self.data):
                        self.add_error(attribute, rule, value)

                if self.should_stop_validating(attribute):
                    break
        return self

    def should_stop_validating(self, attribute):
        if self.has_rule(attribute, "bail"):
            # stop if a message at least has been reported
            return self.messages.has(attribute)

        failed_rules_for_attribute = self.failed_rules.get(attribute, [])

        return (
            self.has_rules(attribute, self.implicit_rules)
            and failed_rules_for_attribute
            and set(failed_rules_for_attribute).intersection(self.implicit_rules)
        )

    def is_required_implied(self, rule):
        name = rule.get_name()
        return name in self.implicit_rules or rule.is_required_implied()

    def should_be_validated(self, attribute, rule, value):
        conditions = [
            self.is_present_or_implicit(attribute, rule, value),
            self.present_if_optional(attribute),
            self.is_not_none_if_nullable(attribute, rule, value),
        ]
        return all(conditions)

    def is_not_none_if_nullable(self, attribute, rule, value):
        if self.has_rule(attribute, "nullable") or self.is_required_implied(rule):
            return True
        # attribute is nullable, so we will check if it is none
        return value != None

    def present_if_optional(self, attribute):
        if not self.has_rule(attribute, "optional"):
            return True

        return self.is_present(attribute)

    def is_present(self, attribute):
        if "*" in attribute:
            # check presence of at least one key
            first_with_attribute = attribute.replace("*", "0")
            return first_with_attribute in self.data
        else:
            return attribute in self.data

    def is_present_or_implicit(self, attribute, rule, value):
        if isinstance(value, str) and len(value) == 0:
            return self.is_required_implied(rule)

        return self.is_present(attribute) or self.is_required_implied(rule)

    def has_rules(self, attribute, rules):
        for rule in rules:
            if self.has_rule(attribute, rule):
                return True
        return False

    def has_rule(self, attribute, rule_name: str):
        rules_for_attribute = self.rules.get(attribute)
        for rule in rules_for_attribute:
            if rule.get_name() == rule_name:
                return True
        return False
        # if isinstance(attr_rules, str) and rule in attr_rules:
        #     return True
        # # not string can be rule objects
        # rules = self.parse_rules(attr_rules)
        # for rule in rules:
        #     if rule.get_name() == rule:
        #         return True
        # return False

    def add_error(self, attribute, rule: "BaseRule", value: "Any"):
        message_with_placeholders = self.get_message(attribute, rule)
        message = self.replace_placeholders_in_message(
            message_with_placeholders, attribute, rule, value
        )
        # add to message bag
        self.messages.add(attribute, message)

        # add to collected failed rules (use defaultdict instead)
        self.failed_rules[attribute] = self.failed_rules.get(attribute, []) + [
            rule.get_name()
        ]

    def get_message(self, attribute, rule) -> str:
        rule_name = rule.get_name()
        attribute_name = self.parent_attributes.get(attribute) or attribute
        # check if custom message has been provided for the attribute
        if self.validation_messages.get(f"{attribute_name}.{rule_name}"):
            return self.validation_messages.get(f"{attribute_name}.{rule_name}")

        # check if custom message has been provided for the rule
        if self.validation_messages.get(rule_name):
            return self.validation_messages.get(rule_name)

        # else if no custom messages have been provided, get the default rule message
        return rule.get_message(attribute)

    def replace_placeholders_in_message(self, message, attribute, rule, value) -> str:
        replacements = {}

        # replace value placeholder
        replacements.update({"value": value})

        # replace attribute placeholder
        replacements.update(
            {"attribute": self.placeholders.get(attribute) or attribute}
        )

        # replace parameters placeholders and additional rules context
        parameters = rule.get_parameters()
        rule_context = rule.with_context()
        if parameters or rule_context:
            replacements = {**parameters, **rule_context, **replacements}

        # replace position and index placeholder
        attr_chunks = attribute.split(".")
        for chunk in attr_chunks:
            if chunk.isnumeric():
                index = int(chunk)
                replacements.update({"position": index + 1, "index": index})

        return message.format_map(replacements)

    def get_value(self, attribute_name: "str"):
        # dotty dict uses : instead of * for wildcards
        attribute_name = attribute_name.replace("*", ":")
        return self.data.get(attribute_name)

    def parse_rules(self, raw_rules: "str|List|Tuple|BaseRule") -> "List[BaseRule]":
        rules = []
        if isinstance(raw_rules, str):
            rules_str = raw_rules.split("|")
            for rule_str in rules_str:
                rule = self.parse_rule_string(rule_str)
                rules.append(rule)
        elif isinstance(raw_rules, (list, tuple)):
            for raw_rule in raw_rules:
                rule = self.parse_rule(raw_rule)
                rules.append(rule)
        elif isinstance(raw_rules, BaseRule):
            rules.append(raw_rules)
        else:
            raise Exception("Validation rules not correct")
        return rules

    def parse_rule_string(self, rule: "str") -> "BaseRule":
        if ":" in rule:
            rule, parameters = rule.split(":")
            rule_class = ValidationFactory().registry[rule]
            # check if named parameters are used
            # TODO: beware of regex, make a check here
            if "=" in parameters:
                parameters_dict = {}
                for param in parameters.split(","):
                    param_name, param_value = param.split("=")
                    parameters_dict.update({param_name: param_value})
                return rule_class(**parameters_dict)
            else:
                parameters_array = parameters.split(",")
                return rule_class(*parameters_array)
        else:
            return ValidationFactory().registry[rule]()

    def parse_rule(self, rule: "str|Any") -> "BaseRule":
        if isinstance(rule, str):
            return self.parse_rule_string(rule)
        elif isinstance(rule, BaseRule):
            return rule
        else:
            raise Exception(f"Unknown rule type: {rule}")

    def errors(self):
        return self.messages.errors()

    def validated(self) -> dict:
        return self.data

    def valid(self):
        return self.messages.empty()

    def invalid(self):
        return not self.valid()

    # def when(self, attribute, rules) -> "Validator":
    #     self._when_rules = explode_rules({attribute: rules})
    #     return self

    # def then(self, attribute, rules) -> "Validator":
    #     self._then_rules = explode_rules({attribute: rules})
    #     return self

    # def run_enclosure(self, enclosure, dictionary):
    #     rule_errors = {}
    #     for rule in enclosure.rules():
    #         rule.handle(dictionary)
    #         for error, message in rule.errors.items():
    #             if error not in rule_errors:
    #                 rule_errors.update({error: message})
    #             else:
    #                 messages = rule_errors[error]
    #                 messages += message
    #                 rule_errors.update({error: messages})
    #         rule.reset()
    #     return rule_errors
