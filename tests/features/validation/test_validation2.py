from tests import TestCase
from src.masonite.validation.ValidatorTwo import Validator
from src.masonite.validation import BaseRule, RuleEnclosure
from src.masonite.facades import Validation


class MasoniteRule(BaseRule):
    def passes(self, value, attribute, dictionary):
        return value == "Masonite"

    def message(self):
        return "{attribute} should be equal to Masonite."

    def negated_message(self):
        return "{attribute} should not be equal to Masonite."


class AcceptedTerms(RuleEnclosure):
    def rules(self):
        return {
            "terms": "required|accepted",
            "email": "required|email",
        }


class TestValidator(TestCase):
    def test_string_rules(self):
        validator = Validator(
            {
                "test": 1,
                "terms": "on",
                "name": "Johnny",
                "other_name": "Joe",
                "age": "25",
            },
            {
                "test": "required|truthy",
                "terms": "accepted",
                "name": "required|length:5,50",
                "other_name": "required|length:min=5,max=50",
                "age": "required|greater_than:18",
            },
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"other_name": ["The other_name length must be between 5 and 50."]},
        )

    def test_dict_rules(self):
        validator = Validator(
            {"test": 1, "terms": "on", "name": "Johnny", "age": "25"},
            {
                "test": "required|truthy",
                "terms": "accepted",
                "name": [
                    "required",
                    Validation.length(min=10),
                ],
                "age": "required|greater_than:18",
            },
        )
        validator.validate()

        self.assertEqual(
            validator.errors(),
            {"name": ["The name must be at least 10 characters."]},
        )

    def test_bail(self):
        validator = Validator(
            {"age": "hello"},
            {
                "age": "bail|numeric|greater_than:18",
            },
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"age": ["The age must be a numeric."]},
        )

        validator = Validator(
            {"age": "hello"},
            {
                "age": "numeric|greater_than:18",
            },
        )
        with self.assertRaises(ValueError) as e:
            validator.validate()

        self.assertTrue("invalid literal for int() with base 10" in str(e.exception))

    def test_custom_message(self):
        validator = Validator(
            {"age": "40"},
            {
                "age": "greater_than:45",
            },
            {"greater_than": "Le champ {attribute} doit être supérieur à {min}."},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"age": ["Le champ age doit être supérieur à 45."]},
        )

        validator = Validator(
            {"age": "40", "count": "1"},
            {
                "age": "greater_than:45",
                "count": "greater_than:45",
            },
            {"age.greater_than": "Le champ {attribute} doit être supérieur à {min}."},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {
                "age": ["Le champ age doit être supérieur à 45."],
                "count": ["The count must be greater than 45."],
            },
        )

        validator = Validator(
            {"age": "40"},
            {
                "age": Validation.greater_than(45).with_message(
                    "Le champ {attribute} doit être supérieur à {min}."
                )
            },
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {
                "age": ["Le champ age doit être supérieur à 45."],
            },
        )

    def test_placeholder(self):
        validator = Validator(
            {"age": "16"},
            {
                "age": "greater_than:18",
            },
            placeholders={"age": "user age"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"age": ["The user age must be greater than 18."]},
        )

    def test_required_if(self):
        validator = Validator(
            {"role": "admin", "type": ""},
            {
                "type": "required_if:role,admin",
            },
        )
        validator.validate()
        self.assertEqual(
            validator.errors(), {"type": ["The type is required because role=admin."]}
        )

    def test_unique_in_db(self):
        validator = Validator(
            {"email": "idmann509@gmail.com"}, {"email": "unique_in_db:users,email"}
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"email": ["A record already exists in table users with the same email."]},
        )

    def test_wildcard_validation(self):
        validator = Validator(
            {
                "users": [
                    {"first_name": "Sam", "last_name": "Girardin"},
                    {"first_name": "John", "last_name": ""},
                    {"first_name": "Joe", "last_name": "Mancuso"},
                ]
            },
            {"users.*.last_name": "required"},
        )

        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"users.1.last_name": ["The users.1.last_name field is required."]},
        )

    def test_required_with(self):
        validator = Validator(
            {"first_name": "Sam", "email": "samgamji@loftr.com"},
            {"email": "required_with:first_name,last_name"},
        )
        validator.validate()
        self.assertTrue(validator.valid())

        validator = Validator(
            {"first_name": "Sam", "email": ""},
            {"email": "required_with:first_name,last_name"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {
                "email": [
                    "The email is required because one in first_name,last_name is present."
                ]
            },
        )

        # with only one argument
        validator = Validator(
            {"first_name": "Sam", "email": ""},
            {"email": "required_with:first_name"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"email": ["The email is required because first_name is present."]},
        )

    def test_password(self):
        validator = Validator(
            {"user_password": "secret"},
            {"password": "strong:16"},
            validation_messages={"password": "Must be {length} long."},
        )
        validator.validate()
        # self.assertEqual(
        #     validator.errors(),
        #     {"user_password": ["The email is required because first_name is present."]},
        # )

    def test_if_validations_should_be_ran(self):
        validator = Validator(
            {},
            {"password": "required|strong:16"},
            validation_messages={"password": "Must be {length} long."},
        )
        validator.validate()

    def test_filled(self):
        validator = Validator(
            {"first_name": ""},
            {"first_name": "filled"},
        )
        validator.validate()

        validator = Validator(
            {},
            {"first_name": "filled"},
        )
        validator.validate()

        validator = Validator(
            {"first_name": "Sam"},
            {"first_name": "filled"},
        )
        validator.validate()

    def test_present(self):
        validator = Validator(
            {"email": ""},
            {"email": "present"},
        )
        validator.validate()
        self.assertTrue(
            validator.valid(),
        )

        validator = Validator(
            {},
            {"email": "present"},
        )
        validator.validate()
        self.assertTrue(
            validator.errors(), {"email": "The email field must be present."}
        )

    def test_optional(self):
        validator = Validator(
            {"email": ""},
            {"email": "optional|required|email"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {"email": ["The email field is required."]},
        )

        validator = Validator(
            {},
            {"email": "optional|required|email"},
        )
        validator.validate()
        self.assertTrue(
            validator.valid(),
        )

    def test_that_if_required_further_validations_wont_be_ran(self):
        validator = Validator({"age": ""}, {"age": "required|numeric"})
        validator.validate()

    def test_required(self):
        validator = Validator({}, {"user": "required"})
        validator.validate()
        self.assertEqual(validator.errors(), {"user": ["The user field is required."]})

        for falsy_value in [[], {}, "", False, 0, None]:
            validator = Validator({"user": falsy_value}, {"user": "required"})
            validator.validate()
            self.assertEqual(
                validator.errors(), {"user": ["The user field is required."]}
            )

    def test_custom_rule(self):
        validator = Validator({"word": "test"}, {"word": [MasoniteRule()]})
        validator.validate()
        self.assertEqual(
            validator.errors(), {"word": ["word should be equal to Masonite."]}
        )

    def test_custom_rule_can_be_mixed_with_others(self):
        validator = Validator({"word": "test"}, {"word": ["length:6", MasoniteRule()]})
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {
                "word": [
                    "The word must be at least 6 characters.",
                    "word should be equal to Masonite.",
                ]
            },
        )

    def test_custom_rule_do_not_imply_required_by_default(self):
        validator = Validator({}, {"word": [MasoniteRule()]})
        validator.validate()
        self.assertTrue(validator.valid())

    def test_custom_rule_can_imply_required(self):
        rule = MasoniteRule()
        rule.required_implied = True
        validator = Validator({}, {"word": [rule]})
        validator.validate()
        self.assertEqual(
            validator.errors(), {"word": ["word should be equal to Masonite."]}
        )

    def test_dictionary(self):
        validator = Validator(
            {"user": {"first_name": "John", "last_name": "Doe"}},
            {"user": "dictionary:first_name,last_name,email,phone"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {
                "user": [
                    "The user field should contains exactly those attributes first_name,last_name,email,phone."
                ]
            },
        )

        validator = Validator(
            {"user": {"first_name": "John", "last_name": "Doe"}},
            {"user": "dictionary:first_name,last_name"},
        )
        validator.validate()
        self.assertTrue(validator.valid())

        validator = Validator(
            {
                "users": [
                    {"id": 1, "first_name": "John", "last_name": "Doe"},
                    {"id": 1, "first_name": "Emilie"},
                ]
            },
            {"users.*": "dictionary:first_name,last_name"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(),
            {
                "users.1": [
                    "The users.1 field should contains exactly those attributes first_name,last_name."
                ]
            },
        )

    def test_matches(self):
        validator = Validator(
            {
                "password": "secret",
                "confirm": "secret",
            },
            {"confirm": "matches:password"},
        )
        validator.validate()
        self.assertTrue(validator.valid())

        validator = Validator(
            {
                "password": "secret",
                "confirm": "no-secret",
            },
            {"confirm": "matches:password"},
        )
        validator.validate()
        self.assertEqual(
            validator.errors(), {"confirm": ["The confirm must match password."]}
        )

    def test_isnt(self):
        validator = Validator(
            {"test": 50}, {"test": Validation.isnt(Validation.in_range(10, 20))}
        )
        validator.validate()
        self.assertTrue(validator.valid())

        validator = Validator(
            {"test": 15}, {"test": Validation.isnt(Validation.in_range(10, 20))}
        )
        validator.validate()
        self.assertEqual(
            validator.errors(), {"test": ["The test must not be between 10 and 20."]}
        )

    def test_when_logic(self):
        validator = Validator(
            {"email": "user@example.com", "phone": "123-456-7890"},
            Validator.when({"email", "required|equals:user@example.com"}).then(
                {"phone": "required"}
            ),
        )
        validator.validate()
        self.dump(validator.errors())

    def test_using_enclosure(self):
        validator = Validator({"email": "user@example.com", "terms": ""}, AcceptedTerms)
        validator.validate()
        self.assertEqual(
            validator.errors(), {"terms": ["The terms field is required."]}
        )

        validator = Validator(
            {"email": "user@example.com", "terms": True}, AcceptedTerms
        )
        validator.validate()
        self.assertTrue(validator.valid())

        validator = Validator(
            {"email": "", "terms": True}, AcceptedTerms, {"email": "optional|email"}
        )
        validator.validate()
        self.assertTrue(validator.valid())
