from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .TestCase import TestCase


class AddCommonAssertions:
    def assertLen(self, iterable: Iterable, length: int) -> "TestCase":
        real_length = len(iterable)
        assert (
            real_length == length
        ), f"Iterable {iterable} is of length {real_length}, not {length}."
        return self
