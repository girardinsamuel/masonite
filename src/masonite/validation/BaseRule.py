from ..utils.structures import data_get


class BaseRule:
    def __init__(self):
        self.attribute_placeholder = None
        self.custom_message = None
        self.negated_custom_message = None
        self.required_implied = False
        # if isinstance(validations, str):
        #     self.validations = [validations]
        # else:
        #     self.validations = validations
        self.errors = {}
        # self.messages = messages
        self.negated = False
        # self.raises = raises

    def passes(self, attribute, key, dictionary):
        return True

    def fails(self, attribute, key, dictionary):
        return not self.passes(attribute, key, dictionary)

    def error(self, key, message):
        if key in self.messages:
            if key in self.errors:
                self.errors[key].append(self.messages[key])
                return
            self.errors.update({key: [self.messages[key]]})
            return

        if not isinstance(message, list):
            self.errors.update({key: [message]})
        else:
            self.errors.update({key: message})

    def find(self, key, dictionary, default=""):
        return data_get(dictionary, key, default)

    def negate(self):
        self.negated = True
        return self

    def raise_exception(self, key):
        if self.raises is not True and key in self.raises:
            error = self.raises.get(key)
            raise error(self.errors[next(iter(self.errors))][0])

        raise ValueError(self.errors[next(iter(self.errors))][0])

    def handle(self, dictionary, attribute, value):
        if self.negated:
            if self.passes(value, attribute, dictionary):
                if hasattr(self, "negated_message"):
                    return self.negated_message(attribute)
                else:
                    return self.message(attribute)
        if not self.passes(value, attribute, dictionary):
            return self.message(attribute)
        return False

    def reset(self):
        self.errors = {}

    def get_name(self):
        return self.__class__.__name__

    def message(self):
        return ""

    def negated_message(self):
        return ""

    def with_message(self, message):
        self.custom_message = message
        return self

    def with_negated_message(self, negated_message):
        self.custom_negated_message = negated_message
        return self

    def with_context(self):
        return {}

    def is_required_implied(self):
        return self.required_implied

    def set_attribute_placeholder(self, placeholder):
        self.attribute_placeholder = placeholder
        return self

    def get_message(self, attribute):
        msg = self.custom_message or self.message()
        return msg

    def get_negated_message(self, attribute):
        msg = self.custom_negated_message or self.negated_message()
        return msg

    def get_parameters(self):
        parameters = {}
        for name, value in self.__dict__.items():
            if name not in [
                "attribute_placeholder",
                "custom_message",
                "negated_custom_message",
                "errors",
                "negated",
                "required_implied",
            ]:
                parameters.update({name: value})

        return parameters
