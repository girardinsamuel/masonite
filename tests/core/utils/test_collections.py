from unittest import TestCase

from src.masonite.utils.collections import Collection, collect


class Person:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @property
    def ref(self):
        return f"# {self.id}"

    def greet(self):
        return f"Hi {self.name}"


class TestCollection(TestCase):
    def test_pluck_(self):
        # data = collect([{"id": 1, "name": "Sam"}, {"id": 2, "name": "Joe"}])
        # self.assertEqual(data.pluck("id"), [1, 2])
        # self.assertEqual(data.pluck("name"), ["Sam", "Joe"])

        data = collect(
            [
                Person(1, "Sam"),
                Person(2, "Joe"),
            ]
        )
        # self.assertEqual(data.pluck("id"), [1, 2])
        # self.assertEqual(data.pluck("name"), ["Sam", "Joe"])
        self.assertEqual(data.pluck("ref"), ["# 1", "# 2"])
