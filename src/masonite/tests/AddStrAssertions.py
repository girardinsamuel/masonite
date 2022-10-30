from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .TestCase import TestCase


class AddStrAssertions:
    def assertStartsWith(self, string: str, reference: str) -> "TestCase":
        assert string.startswith(
            reference
        ), f"String {string} does not start with {reference}."
        return self

    def assertEndsWith(self, string: str, reference: str) -> "TestCase":
        assert string.endswith(
            reference
        ), f"String {string} does not end with {reference}."
        return self
