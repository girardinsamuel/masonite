import os

from tests import TestCase
from src.masonite.input import InputBag
from src.masonite.tests import MockInput
from src.masonite.utils.http import RequestFile, generate_wsgi_form_data


class TestInputBag(TestCase):
    def test_can_parse_query_string(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "hello=you&goodbye=me"})
        self.assertEqual(bag.get("hello"), "you")
        self.assertEqual(bag.get("goodbye"), "me")

    def test_can_parse_post_data(self):
        bag = InputBag()
        bag.load(generate_wsgi_form_data({"__token": 1}))
        self.assertEqual(bag.get("__token"), 1)

    def test_can_parse_duplicate_values(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "filter[name]=Joe&filter[last]=Bill"})
        self.assertTrue("name" in bag.get("filter"))
        self.assertTrue("last" in bag.get("filter"))

    def test_all_with_values(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "hello=you"})
        self.assertEqual(bag.all_as_values(), {"hello": "you"})

    def test_can_get_defaults(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": ""})
        self.assertEqual(bag.get("hello", "default"), "default")
        self.assertEqual(
            bag.get("hello"), None
        )  # TODO: This should probably return a blank string instead of None
        self.assertEqual(bag.get("hello[]"), [])

    def test_all_without_internal_values(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "hello=you&__token=tok"})
        self.assertEqual(bag.all_as_values(internal_variables=False), {"hello": "you"})

    def test_has(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "hello=you&goodbye=me"})
        self.assertTrue(bag.has("hello", "goodbye"))

    def test_only(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "hello=you&goodbye=me&name=Joe"})
        self.assertEqual(bag.only("hello", "name"), {"hello": "you", "name": "Joe"})

    def test_only_array_based_inputs(self):
        bag = InputBag()
        bag.load({"QUERY_STRING": "user[]=user1&user[]=user2"})
        self.assertEqual(bag.get("user[]"), ["user1", "user2"])
        bag = InputBag()
        bag.load({"QUERY_STRING": "user[user1]=value&user[user2]=value"})
        self.assertEqual(bag.get("user"), {"user1": "value", "user2": "value"})

    def test_can_parse_text_plain_content_type(self):
        post_data = MockInput(
            '{"param": "hey", "foo": [9, 8, 7, 6], "bar": "baz"}'.encode("utf-8")
        )
        bag = InputBag()
        bag.load({"wsgi.input": post_data, "CONTENT_TYPE": "text/plain"})
        self.assertEqual(bag.get("param"), "hey")

    def test_can_parse_application_json_content_type(self):
        data = generate_wsgi_form_data(
            {"param": "hey", "foo": [9, 8, 7, 6], "bar": "baz"}
        )
        bag = InputBag()
        bag.load(data)
        self.assertEqual(bag.get("param"), "hey")
        self.assertEqual(bag.get("foo"), [9, 8, 7, 6])

    def test_can_parse_form_urlencoded_content_type(self):
        data = generate_wsgi_form_data(
            {"jack": "Daniels"}, content_type="application/x-www-form-urlencoded"
        )
        bag = InputBag()
        bag.load(data)
        self.assertEqual(bag.get("jack"), "Daniels")

    def test_can_parse_multipart_formdata_content_type(self):
        data = generate_wsgi_form_data(
            {"key": "value", "test": 1}, content_type="multipart/form-data"
        )
        bag = InputBag()
        bag.load(data)
        import pdb

        pdb.set_trace()
        self.assertEqual(bag.get("key"), "value")
        self.assertEqual(bag.get("test"), "1")

    def test_advanced_dict_parse(self):
        bag = InputBag()
        inputs = bag.parse_dict(
            {"user[][name]": ["Joe"], "user[][email]": ["joe@masoniteproject.com"]}
        )
        self.assertEqual(
            inputs, {"user": [{"name": "Joe"}, {"email": "joe@masoniteproject.com"}]}
        )
        inputs = bag.parse_dict(
            {"user[name]": ["Joe"], "user[email]": ["joe@masoniteproject.com"]}
        )
        self.assertEqual(
            inputs, {"user": {"email": "joe@masoniteproject.com", "name": "Joe"}}
        )

    def test_can_parse_nested_post_data(self):
        data = generate_wsgi_form_data({"key": "val", "a": {"b": {"c": 1}}})
        bag = InputBag()
        bag.load(data)
        self.assertEqual(bag.get("key"), "val")
        self.assertEqual(bag.get("a.b.c"), 1)

    def test_can_parse_files_with_multipart_form_data_encoding(self):
        data = generate_wsgi_form_data(
            {"name": "sam", "avatar": RequestFile("avatar.png", "image/png", "hello")},
            "multipart/form-data",
        )
        bag = InputBag()
        bag.load(data)
        # can parse normal data
        self.assertEqual(bag.get("name"), "sam")
        # can parse file data
        self.assertIsInstance(bag.get("avatar"), UploadedFile)
        self.assertEqual(bag.get("avatar").filename, "avatar.png")
        self.assertEqual(bag.get("avatar").get_original_mimetype(), "image/png")
        self.assertEqual(bag.get("avatar").get_content(), "hello")

    def test_can_parse_files_with_form_urlencoded_encoding(self):
        pass
