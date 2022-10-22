import re
import os
import mimetypes

from ..filesystem import UploadedFile

from ..configuration import config
from ..facades import Loader
from .BaseRule import BaseRule


class required(BaseRule):
    def passes(self, value, attribute, dictionary):
        """The passing criteria for this rule.

        The key must exist in the dictionary and return a True boolean value.
        The key can use * notation.

        Arguments:
            attribute {mixed} -- The value found within the dictionary
            key {string} -- The key in the dictionary being searched for.
            dictionary {dict} -- The dictionary being searched

        Returns:
            bool
        """
        return value

    def message(self):
        """A message to show when this rule fails

        Arguments:
            key {string} -- The key used to search the dictionary

        Returns:
            string
        """
        return "The {attribute} field is required."

    def negated_message(self):
        """A message to show when this rule is negated using a negation rule like 'isnt()'

        For example if you have a message that says 'this is required' you may have a negated statement
        that says 'this is not required'.

        Arguments:
            key {string} -- The key used to search the dictionary

        Returns:
            string
        """
        return "The {attribute} field is not required."


class filled(BaseRule):
    """If the attribute is present, it must be filled (not empty)."""

    def passes(self, value, attribute, dictionary):
        # TODO: check this with * ?
        if attribute in dictionary:
            return required().passes(value, attribute, dictionary)
        return True

    def message(self):
        return "The {attribute} field must have a value."

    def negated_message(self):
        return "The {attribute} field must not have a value."


class present(BaseRule):
    """The attribute must be present in the validated data but can be empty."""

    def passes(self, value, attribute, dictionary):
        # TODO: check this with * ?
        return attribute in dictionary

    def message(self):
        return "The {attribute} field must be present."

    def message(self):
        return "The {attribute} field must not be present."


class timezone(BaseRule):
    def passes(self, attribute, key, dictionary):
        import pytz

        return attribute in pytz.all_timezones

    def message(self, attribute):
        return "The {} must be a valid timezone.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a valid timezone.".format(attribute)


class one_of(BaseRule):
    def passes(self, attribute, key, dictionary):
        for validation in self.validations:
            if validation in dictionary:
                return True

        return False

    def message(self, attribute):
        if len(self.validations) > 2:
            text = ", ".join(self.validations)
        else:
            text = " or ".join(self.validations)

        return "The {} is required.".format(text)

    def negated_message(self, attribute):
        if len(self.validations) > 2:
            text = ", ".join(self.validations)
        else:
            text = " or ".join(self.validations)

        return "The {} is not required.".format(text)


class boolean(BaseRule):
    def passes(self, attribute, key, dictionary):
        return attribute in [True, False, 0, 1, "0", "1"]

    def message(self, attribute):
        return "The {} must be a boolean.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a boolean.".format(attribute)


class accepted(BaseRule):
    def passes(self, value, attribute, dictionary):
        return (
            value is True
            or value == "on"
            or value == "yes"
            or value == "1"
            or value == 1
        )

    def message(self):
        return "The {attribute} must be accepted."

    def negated_message(self):
        return "The {attribute} must not be accepted."


class ip(BaseRule):
    def passes(self, attribute, key, dictionary):
        import socket

        try:
            socket.inet_aton(attribute)
            return True
        except socket.error:
            return False

    def message(self, attribute):
        return "The {} must be a valid ipv4 address.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a valid ipv4 address.".format(attribute)


class date(BaseRule):
    def passes(self, attribute, key, dictionary):
        import pendulum

        try:
            date = pendulum.parse(attribute)
            return date
        except pendulum.parsing.exceptions.ParserError:
            return False

    def message(self, attribute):
        return "The {} must be a valid date.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a valid date.".format(attribute)


class before_today(BaseRule):
    def __init__(self, validations, tz="UTC", messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.tz = tz

    def passes(self, attribute, key, dictionary):
        import pendulum

        try:
            return pendulum.parse(attribute, tz=self.tz) <= pendulum.yesterday()
        except pendulum.parsing.exceptions.ParserError:
            return False

    def message(self, attribute):
        return "The {} must be a date before today.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a date before today.".format(attribute)


class after_today(BaseRule):
    def __init__(self, validations, tz="Universal", messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.tz = tz

    def passes(self, attribute, key, dictionary):
        import pendulum

        try:
            return pendulum.parse(attribute, tz=self.tz) >= pendulum.yesterday()
        except pendulum.parsing.exceptions.ParserError:
            return False

    def message(self, attribute):
        return "The {} must be a date after today.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a date after today.".format(attribute)


class is_past(BaseRule):
    def __init__(self, validations, tz="Universal", messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.tz = tz

    def passes(self, attribute, key, dictionary):
        import pendulum

        try:
            return pendulum.parse(attribute, tz=self.tz).is_past()
        except pendulum.parsing.exceptions.ParserError:
            return False

    def message(self, attribute):
        return "The {} must be a time in the past.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a time in the past.".format(attribute)


class is_future(BaseRule):
    def __init__(self, validations, tz="Universal", messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.tz = tz

    def passes(self, attribute, key, dictionary):
        import pendulum

        try:
            return pendulum.parse(attribute, tz=self.tz).is_future()
        except pendulum.parsing.exceptions.ParserError:
            return False

    def message(self, attribute):
        return "The {} must be a time in the past.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a time in the past.".format(attribute)


class email(BaseRule):
    def passes(self, value, attribute, dictionary):
        return re.compile(
            r"^[^.][^@]*@([?)[a-zA-Z0-9-.])+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$"
        ).match(value)

    def message(self):
        return "The {attribute} must be a valid email address."

    def negated_message(self):
        return "The {attribute} must not be a valid email address."


class nullable(BaseRule):
    """Don't check subsequent validation rules for this attribute if attribute is '' or None."""

    def passes(self, value, attribute, dictionary):
        return True


class matches(BaseRule):
    def __init__(self, match):
        super().__init__()
        self.match = match

    def passes(self, value, attribute, dictionary):
        return value == dictionary.get(self.match)

    def message(self):
        return "The {attribute} must match {match}."

    def negated_message(self, attribute):
        return "The {attribute} must not match {match}."


class exists(BaseRule):
    def passes(self, attribute, key, dictionary):
        return key in dictionary

    def message(self, attribute):
        return "The {} must exist.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not exist.".format(attribute)


def resolve_model_or_table(string):
    # it means that a python model path has been given
    if "." in string:
        model_name = string.split(".")[-1]
        model_class = Loader.get_object(string, model_name)
        table = model_class().get_table_name()
        return table, model_class
    else:
        return string, None


class exists_in_db(BaseRule):
    """A record with field equal to the given value should exists in the table/model specified."""

    def __init__(
        self,
        validations,
        table_or_model,
        column=None,
        connection="default",
        messages={},
        raises={},
    ):
        super().__init__(validations, messages=messages, raises=raises)
        self.connection = config("database.db").get_query_builder(connection)
        self.column = column
        self.table, self.model = resolve_model_or_table(table_or_model)

    def passes(self, attribute, key, dictionary):
        column = key if not self.column else self.column
        count = self.connection.table(self.table).where(column, attribute).count()
        return count

    def message(self, attribute):
        return "No record found in table {} with the same {}.".format(
            self.table, attribute
        )

    def negated_message(self, attribute):
        return "A record already exists in table {} with the same {}.".format(
            self.table, attribute
        )


class not_exists_in_db(BaseRule):
    """A record with field equal to the given value should exists in the table/model specified."""

    def __init__(
        self,
        validations,
        table_or_model,
        column=None,
        connection="default",
        messages={},
        raises={},
    ):
        super().__init__(validations, messages=messages, raises=raises)
        self.connection = config("database.db").get_query_builder(connection)
        self.column = column
        self.table, self.model = resolve_model_or_table(table_or_model)

    def passes(self, attribute, key, dictionary):
        column = key if not self.column else self.column
        count = self.connection.table(self.table).where(column, attribute).count()
        return count == 0

    def message(self, attribute):
        return "A record already exists in table {} with the same {}".format(
            self.table, attribute
        )

    def negated_message(self, attribute):
        return "No record found in table {} with the same {}".format(
            self.table, attribute
        )


class unique_in_db(BaseRule):
    """No record should exist for the field under validation within the given table/model."""

    def __init__(
        self,
        table_or_model,
        column=None,
        connection="default",
    ):
        super().__init__()
        self.connection = config("database.db").get_query_builder(connection)
        self.column = column
        self.table, self.model = resolve_model_or_table(table_or_model)

    def passes(self, value, attribute, dictionary):
        column = attribute if not self.column else self.column
        count = self.connection.table(self.table).where(column, value).count()
        return count == 0

    def message(self):
        return "A record already exists in table {table} with the same {attribute}."

    def negated_message(self):
        return "A record should exist in table {table} with the same {attribute}."


class active_domain(BaseRule):
    def passes(self, attribute, key, dictionary):
        import socket

        try:
            if "@" in attribute:
                # validation is for an email address
                return socket.gethostbyname(attribute.split("@")[1])

            return socket.gethostbyname(
                attribute.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            )
        except socket.gaierror:
            return False

    def message(self, attribute):
        return "The {} must be an active domain name.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be an active domain name.".format(attribute)


class numeric(BaseRule):
    def passes(self, attribute, key, dictionary):
        if isinstance(attribute, list):
            for value in attribute:
                if not str(value).replace(".", "", 1).isdigit():
                    return False
        else:
            return str(attribute).replace(".", "", 1).isdigit()

        return True

    def message(self):
        return "The {attribute} must be a numeric."

    def negated_message(self):
        return "The {attribute} must not be a numeric."


class is_list(BaseRule):
    def passes(self, attribute, key, dictionary):
        return isinstance(attribute, list)

    def message(self, attribute):
        return "The {} must be a list.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a list.".format(attribute)


class string(BaseRule):
    def passes(self, attribute, key, dictionary):
        if isinstance(attribute, list):
            for attr in attribute:
                if not isinstance(attr, str):
                    return False

            return True

        return isinstance(attribute, str)

    def message(self, attribute):
        return "The {} must be a string.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a string.".format(attribute)


class none(BaseRule):
    def passes(self, attribute, key, dictionary):
        return attribute is None

    def message(self, attribute):
        return "The {} must be None.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be None.".format(attribute)


class bail(BaseRule):
    def passes(self, attribute, key, dictionary):
        return True


class optional(BaseRule):
    def passes(self, attribute, key, dictionary):
        return True


class length(BaseRule):
    def __init__(self, min=0, max=False):
        super().__init__()
        self.min = int(min)
        self.max = int(max)

    def passes(self, attribute, key, dictionary):
        if not hasattr(attribute, "__len__"):
            attribute = str(attribute)
        if self.max:
            return len(attribute) >= self.min and len(attribute) <= self.max
        else:
            return len(attribute) >= self.min

    def message(self):
        if self.min and not self.max:
            return "The {attribute} must be at least {min} characters."
        else:
            return "The {attribute} length must be between {min} and {max}."

    def negated_message(self):
        if self.min and not self.max:
            return "The {attribute} must be {min} characters maximum."
        else:
            return "The {attribute} length must not be between {min} and {max}."


class in_range(BaseRule):
    def __init__(self, min=1, max=255):
        super().__init__()
        self.min = min
        self.max = max

    def passes(self, value, attribute, dictionary):
        value = str(value)
        if value.isalpha():
            return False

        if "." in value:
            try:
                value = float(value)
            except Exception:
                pass

        elif value.isdigit():
            value = int(value)

        return value >= self.min and value <= self.max

    def message(self):
        return "The {attribute} must be between {min} and {max}."

    def negated_message(self, attribute):
        return "The {attribute} must not be between {min} and {max}."


class equals(BaseRule):
    def __init__(self, compared_value):
        super().__init__()
        self.compared_value = compared_value

    def passes(self, value, attribute, dictionary):
        return value == self.compared_value

    def message(self):
        return "The {attribute} must be equal to {compared_value}."

    def negated_message(self):
        return "The {attribute} must not be equal to {compared_value}."


class is_in(BaseRule):
    def __init__(self, validations, value="", messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.value = value

    def passes(self, attribute, key, dictionary):
        return attribute in self.value

    def message(self, attribute):
        return "The {} must contain an element in {}.".format(attribute, self.value)

    def negated_message(self, attribute):
        return "The {} must not contain an element in {}.".format(attribute, self.value)


class greater_than(BaseRule):
    def __init__(self, min):
        super().__init__()
        self.min = int(min)

    def message(self):
        return "The {attribute} must be greater than {min}."

    def passes(self, value, attribute, dictionary):
        return int(value) > int(self.min)


class less_than(BaseRule):
    def __init__(self, validations, value="", messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.value = value

    def passes(self, attribute, key, dictionary):
        return attribute < self.value

    def message(self, attribute):
        return "The {} must be less than {}.".format(attribute, self.value)

    def negated_message(self, attribute):
        return "The {} must not be less than {}.".format(attribute, self.value)


class strong(BaseRule):
    def __init__(
        self,
        length=8,
        uppercase=2,
        lowercase=2,
        numbers=2,
        special=2,
        special_chars=None,
        breach=False,
    ):
        super().__init__()
        self.length = int(length)
        self.uppercase = int(uppercase)
        self.lowercase = int(lowercase)
        self.numbers = int(numbers)
        self.special = int(special)
        self.special_chars = special_chars
        self.breach = breach

        self.length_check = True
        self.uppercase_check = True
        self.lowercase_check = True
        self.numbers_check = True
        self.special_check = True
        self.breach_check = True

    def passes(self, attribute, key, dictionary):
        all_clear = True

        if len(attribute) < self.length:
            all_clear = False
            self.length_check = False

        if self.uppercase != 0:
            uppercase = 0
            for letter in attribute:
                if letter.isupper():
                    uppercase += 1

            if uppercase < self.uppercase:
                self.uppercase_check = False
                all_clear = False

        if self.lowercase != 0:
            lowercase = 0
            for letter in attribute:
                if letter.islower():
                    lowercase += 1

            if lowercase < self.lowercase:
                self.lowercase_check = False
                all_clear = False

        if self.numbers != 0:
            numbers = 0
            for letter in attribute:
                if letter.isdigit():
                    numbers += 1

            if numbers < self.numbers:
                self.numbers_check = False
                all_clear = False

        if self.breach:
            try:
                from pwnedapi import Password
            except ImportError:
                raise ImportError(
                    "Checking for breaches requires the 'pwnedapi' library. Please install it with 'pip install pwnedapi'"
                )

            password = Password(attribute)
            if password.is_pwned():
                self.breach_check = False
                all_clear = False

        if self.special != 0:
            special_chars = "[^A-Za-z0-9]"
            if self.special_chars:
                special_chars = f"[{self.special_chars}]"
            if len(re.findall(special_chars, attribute)) < self.special:
                self.special_check = False
                all_clear = False

        return all_clear

    def message(self):
        if not self.length_check:
            return "The {attribute} field must be {length} characters in length."
        if not self.uppercase_check:
            return "The {attribute} field must have {uppercase} uppercase letters."

        # if not self.lowercase_check:
        #     message.append(
        #         "The {} field must have {} lowercase letters".format(
        #             attribute, self.lowercase
        #         )
        #     )

        # if not self.special_check:
        #     valid_chars = self.special_chars or "!@#$%^&*()_+"
        #     message.append(
        #         "The {} field must contain at least {} of these characters: '{}'".format(
        #             attribute, self.special, valid_chars
        #         )
        #     )

        # if not self.numbers_check:
        #     message.append(
        #         "The {} field must have {} numbers".format(attribute, self.numbers)
        #     )

        # if not self.breach_check:
        #     message.append(
        #         "The {} field has been breached in the past. Try another {}".format(
        #             attribute, attribute
        #         )
        #     )

    def negated_message(self):
        return "The {attribute} must not be less than {length}."


class isnt(BaseRule):
    def __init__(self, *rules):
        super().__init__()
        self.rules = rules

    def passes(self, value, attribute, dictionary):
        for rule in self.rules:
            if not rule.fails(value, attribute, dictionary):
                return False
        return True

    def message(self):
        return "The {attribute} field ..."

    # def handle(self, dictionary):
    #     for rule in self.validations:
    #         rule.negate().handle(dictionary)
    #         self.errors.update(rule.errors)


class does_not(BaseRule):
    def __init__(self, *rules, messages={}, raises={}):
        super().__init__(rules)
        self.should_run_then = True

    def handle(self, dictionary):
        self.dictionary = dictionary
        errors = False
        for rule in self.validations:
            if rule.handle(dictionary):
                errors = True

        if not errors:
            for rule in self.then_rules:
                if not rule.handle(dictionary):
                    self.errors.update(rule.errors)

    def then(self, *rules):
        self.then_rules = rules
        return self


class dictionary(BaseRule):
    def __init__(self, *keys):
        super().__init__()
        self.keys = keys

    def passes(self, value, attribute, dictionary):
        if not isinstance(value, dict):
            return False
        for key in self.keys:
            if key not in value:
                return False
        return True

    def with_context(self):
        return {"attributes": ",".join(self.keys)}

    def message(self):
        return "The {attribute} field should contains exactly those attributes {attributes}."

    def negated_message(self):
        return "The {attribute} field should not contain those attributes {attributes} exactly."


class when(BaseRule):
    def __init__(self, *rules, messages={}, raises={}):
        super().__init__(rules)
        self.should_run_then = True

    def handle(self, dictionary):
        self.dictionary = dictionary
        errors = False
        for rule in self.validations:
            if rule.handle(dictionary):
                errors = True

        if errors:
            for rule in self.then_rules:
                if not rule.handle(dictionary):
                    self.errors.update(rule.errors)

    def then(self, *rules):
        self.then_rules = rules
        return self


class truthy(BaseRule):
    def passes(self, attribute, key, dictionary):
        return attribute

    def message(self, attribute):
        return "The {} must be a truthy value.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a truthy value.".format(attribute)


class json(BaseRule):
    def passes(self, attribute, key, dictionary):
        import json as json_module

        try:
            return json_module.loads(str(attribute))
        except (TypeError, json_module.decoder.JSONDecodeError):
            return False

    def message(self, attribute):
        return "The {} must be a valid JSON.".format(attribute)

    def negated_message(self, attribute):
        return "The {} must not be a valid JSON.".format(attribute)


class phone(BaseRule):
    def __init__(self, *rules, pattern="123-456-7890", messages={}, raises={}):
        super().__init__(rules, messages=messages, raises=raises)
        # 123-456-7890
        # (123)456-7890
        self.pattern = pattern

    def passes(self, attribute, key, dictionary):
        if self.pattern == "(123)456-7890":
            return re.compile(r"^\(\w{3}\)\w{3}\-\w{4}$").match(attribute)
        elif self.pattern == "123-456-7890":
            return re.compile(r"^\w{3}\-\w{3}\-\w{4}$").match(attribute)

    def message(self, attribute):
        if self.pattern == "(123)456-7890":
            return "The {} must be in the format (XXX)XXX-XXXX.".format(attribute)
        elif self.pattern == "123-456-7890":
            return "The {} must be in the format XXX-XXX-XXXX.".format(attribute)

    def negated_message(self, attribute):
        if self.pattern == "(123)456-7890":
            return "The {} must not be in the format (XXX)XXX-XXXX.".format(attribute)
        elif self.pattern == "123-456-7890":
            return "The {} must not be in the format XXX-XXX-XXXX.".format(attribute)


class confirmed(BaseRule):
    def passes(self, value, attribute, dictionary):
        if attribute in dictionary and attribute + "_confirmation" in dictionary:
            return value == dictionary["{}".format(attribute + "_confirmation")]
        return False

    def message(self):
        return "The {attribute} confirmation does not match."

    def negated_message(self):
        return "The {attribute} confirmation matches."


class regex(BaseRule):
    def __init__(self, validations, pattern, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.pattern = pattern

    def passes(self, attribute, key, dictionary):
        return re.compile(r"{}".format(self.pattern)).match(attribute)

    def message(self, attribute):
        return "The {} does not match pattern {} .".format(attribute, self.pattern)

    def negated_message(self, attribute):
        return "The {} matches pattern {} .".format(attribute, self.pattern)


def parse_size(size):
    """Parse humanized size into bytes"""
    from hfilesize import FileSize

    return FileSize(size, case_sensitive=False)


class BaseFileValidation(BaseRule):
    def __init__(self, validations, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.file_check = True
        self.size_check = True
        self.mimes_check = True
        self.all_clear = True

    def passes(self, attribute, key, dictionary):
        # Here we can validate on a filepath or an uploaded file (from request)
        if isinstance(attribute, UploadedFile):
            filepath = attribute.name
            file_size = attribute.size
        else:
            filepath = attribute
            if not os.path.isfile(filepath):
                self.file_check = False
                return False
            file_size = os.path.getsize(filepath)
        # validate size
        if self.size:
            if file_size > self.size:
                self.size_check = False
                self.all_clear = False
        # validate extension
        if self.allowed_extensions:
            mimetype, encoding = mimetypes.guess_type(filepath)
            if mimetype not in self.allowed_mimetypes:
                self.mimes_check = False
                self.all_clear = False
        return self.all_clear


class file(BaseFileValidation):
    def __init__(self, validations, size=False, mimes=False, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.size = parse_size(size)

        # parse allowed extensions to a list of mime types
        self.allowed_extensions = mimes
        if mimes:
            self.allowed_mimetypes = list(
                map(lambda mt: mimetypes.types_map.get("." + mt, None), mimes)
            )

    def message(self, attribute):
        messages = []
        if not self.file_check:
            messages.append("The {} is not a valid file.".format(attribute))

        if not self.size_check:
            from hfilesize import FileSize

            messages.append(
                "The {} file size exceeds {:.02fH}.".format(
                    attribute, FileSize(self.size)
                )
            )
        if not self.mimes_check:
            messages.append(
                "The {} mime type is not valid. Allowed formats are {}.".format(
                    attribute, ",".join(self.allowed_extensions)
                )
            )

        return messages

    def negated_message(self, attribute):
        messages = []
        if self.file_check:
            messages.append("The {} is a valid file.".format(attribute))
        if self.size_check:
            from hfilesize import FileSize

            messages.append(
                "The {} file size is less or equal than {:.02fH}.".format(
                    attribute, FileSize(self.size)
                )
            )
        if self.mimes_check:
            messages.append(
                "The {} mime type is in {}.".format(
                    attribute, ",".join(self.allowed_extensions)
                )
            )
        return messages


class image(BaseFileValidation):
    def __init__(self, validations, size=False, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.size = parse_size(size)
        image_mimetypes = {
            ext: mimetype
            for ext, mimetype in mimetypes.types_map.items()
            if mimetype.startswith("image")
        }
        self.allowed_extensions = list(image_mimetypes.keys())
        self.allowed_mimetypes = list(image_mimetypes.values())

    def message(self, attribute):
        messages = []
        if not self.file_check:
            messages.append("The {} is not a valid file.".format(attribute))

        if not self.size_check:
            from hfilesize import FileSize

            messages.append(
                "The {} file size exceeds {:.02fH}.".format(
                    attribute, FileSize(self.size)
                )
            )

        if not self.mimes_check:
            messages.append(
                "The {} file is not a valid image. Allowed formats are {}.".format(
                    attribute, ",".join(self.allowed_extensions)
                )
            )

        return messages

    def negated_message(self, attribute):
        messages = []
        if self.file_check:
            messages.append("The {} is a valid file.".format(attribute))
        if self.size_check:
            from hfilesize import FileSize

            messages.append(
                "The {} file size is less or equal than {:.02fH}.".format(
                    attribute, FileSize(self.size)
                )
            )

        if self.mimes_check:
            messages.append("The {} file is a valid image.".format(attribute))

        return messages


class video(BaseFileValidation):
    def __init__(self, validations, size=False, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.size = parse_size(size)

        video_mimetypes = {
            ext: mimetype
            for ext, mimetype in mimetypes.types_map.items()
            if mimetype.startswith("video")
        }

        self.allowed_extensions = list(video_mimetypes.keys())
        self.allowed_mimetypes = list(video_mimetypes.values())

    def message(self, attribute):
        messages = []
        if not self.file_check:
            messages.append("The {} is not a valid file.".format(attribute))

        if not self.size_check:
            from hfilesize import FileSize

            messages.append(
                "The {} file size exceeds {:.02fH}.".format(
                    attribute, FileSize(self.size)
                )
            )

        if not self.mimes_check:
            messages.append(
                "The {} file is not a valid video. Allowed formats are {}.".format(
                    attribute, ",".join(self.allowed_extensions)
                )
            )

        return messages

    def negated_message(self, attribute):
        messages = []
        if self.file_check:
            messages.append("The {} is a valid file.".format(attribute))

        if self.size_check:
            from hfilesize import FileSize

            messages.append(
                "The {} file size is less or equal than {:.02fH}.".format(
                    attribute, FileSize(self.size)
                )
            )

        if self.mimes_check:
            messages.append("The {} file is a valid video.".format(attribute))

        return messages


class postal_code(BaseRule):
    def __init__(self, validations, locale, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        from .resources.postal_codes import PATTERNS

        self.locales = []
        self.patterns = []
        self.patterns_example = []
        self.locales = locale.split(",")

        for locale in self.locales:
            pattern_dict = PATTERNS.get(locale, None)
            if pattern_dict is None or pattern_dict["pattern"] is None:
                raise NotImplementedError(
                    "Unsupported country code {}. Check that it is a ISO 3166-1 country code or open a PR to require support of this country code.".format(
                        locale
                    )
                )
            else:
                self.patterns.append(pattern_dict["pattern"])
                self.patterns_example.append(pattern_dict["example"])

    def passes(self, attribute, key, dictionary):
        for pattern in self.patterns:
            # check that at least one pattern match attribute
            if re.compile(r"{}".format(pattern)).match(attribute):
                return True
        return False

    def message(self, attribute):
        return "The {} is not a valid {} postal code. Valid {} {}.".format(
            attribute,
            ",".join(self.locales),
            "examples are" if len(self.locales) > 1 else "example is",
            ",".join(self.patterns_example),
        )

    def negated_message(self, attribute):
        return "The {} is a valid {} postal code.".format(attribute, self.locale)


class different(BaseRule):
    """The field under validation must be different than an other given field."""

    def __init__(self, validations, other_field, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.other_field = other_field

    def passes(self, attribute, key, dictionary):
        other_value = dictionary.get(self.other_field, None)
        return attribute != other_value

    def message(self, attribute):
        return "The {} value must be different than {} value.".format(
            attribute, self.other_field
        )

    def negated_message(self, attribute):
        return "The {} value be the same as {} value.".format(
            attribute, self.other_field
        )


class uuid(BaseRule):
    """The field under validation must be a valid UUID. The UUID version standard
    can be precised (1,3,4,5)."""

    def __init__(self, validations, version=4, messages={}, raises={}):
        super().__init__(validations, messages=messages, raises=raises)
        self.version = version
        self.uuid_type = "UUID"
        if version:
            self.uuid_type = "UUID {0}".format(self.version)

    def passes(self, attribute, key, dictionary):
        from uuid import UUID

        try:
            uuid_value = UUID(str(attribute))
            return uuid_value.version == int(self.version)
        except ValueError:
            return False

    def message(self, attribute):
        return "The {} value must be a valid {}.".format(attribute, self.uuid_type)

    def negated_message(self, attribute):
        return "The {} value must not be a valid {}.".format(attribute, self.uuid_type)


class required_if(BaseRule):
    """The field under validation must be present and not empty only
    if an other field has a given value."""

    def __init__(self, other_field, other_value):
        super().__init__()
        self.other_field = other_field
        self.other_value = other_value

    def passes(self, value, attribute, dictionary):
        if self.find(self.other_field, dictionary) == self.other_value:
            return required.passes(self, value, attribute, dictionary)
        return True

    def message(self):
        return "The {attribute} is required because {other_field}={other_value}."

    def negated_message(self):
        return "The {attribute} is not required because {other_field}={other_value} or {other_field} is not present."


class required_with(BaseRule):
    """The field under validation must be present and not empty only
    if any of the other specified fields are present."""

    def __init__(self, *other_fields):
        super().__init__()
        self.other_fields = other_fields

    def passes(self, attribute, key, dictionary):
        for field in self.other_fields:
            if field in dictionary:
                return required.passes(self, attribute, key, dictionary)
        else:
            return True

    def with_context(self):
        return {"other_fields": ",".join(self.other_fields)}

    def message(self):
        if len(self.other_fields) > 1:
            return (
                "The {attribute} is required because one in {other_fields} is present."
            )
        else:
            return "The {attribute} is required because {other_fields} is present."

    def negated_message(self):
        if len(self.other_fields) > 1:
            return "The {attribute} is not required because none of {other_fields} is not present."
        else:
            return (
                "The {attribute} is not required because {other_fields} is not present."
            )


class distinct(BaseRule):
    """When working with list, the field under validation must not have any
    duplicate values."""

    def passes(self, attribute, key, dictionary):
        # check if list contains duplicates
        return len(set(attribute)) == len(attribute)

    def message(self, attribute):
        return "The {} field has duplicate values.".format(attribute)

    def negated_message(self, attribute):
        return "The {} field has only different values.".format(attribute)


class ValidationFactory:

    registry = {}

    def __init__(self):
        self.register(
            accepted,
            bail,
            boolean,
            active_domain,
            after_today,
            before_today,
            confirmed,
            # contains, TODO: alias exists ?
            date,
            does_not,
            dictionary,
            different,
            distinct,
            equals,
            email,
            exists,
            exists_in_db,
            not_exists_in_db,
            file,
            filled,
            greater_than,
            image,
            in_range,
            is_future,
            is_in,
            isnt,
            is_list,
            is_past,
            ip,
            json,
            length,
            less_than,
            matches,
            none,
            numeric,
            nullable,
            one_of,
            optional,
            phone,
            postal_code,
            present,
            regex,
            required,
            required_if,
            required_with,
            string,
            strong,
            timezone,
            truthy,
            unique_in_db,
            uuid,
            video,
            when,
        )

    def register(self, *cls):
        for obj in cls:
            self.registry.update({obj.__name__: obj})
