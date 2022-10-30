import os
from tests import TestCase

from src.masonite.tests import TestFilesAndDirs
from src.masonite.filesystem import File, UploadedFile
from src.masonite.utils.filesystem import FileSystem
from src.masonite.utils.location import base_path


class TestLocalStorage(TestCase, TestFilesAndDirs):
    def setUp(self):
        super().setUp()
        # build a local test driver using a temporary directory
        self.driver = self.application.make("storage").build(
            "file", {"path": base_path(self.get_root())}
        )
        self.document = UploadedFile("doc.pdf", "hello", "application/pdf")

    def test_can_put_string(self):
        self.driver.put("key.log", "value")
        self.assertTrue(self.driver.exists("key.log"))
        self.assertEqual(self.driver.get("key.log"), "value")

    def test_can_put_bytes(self):
        self.driver.put("key.log", b"value")
        self.assertEqual(self.driver.get("key.log"), "value")

    def test_can_put_file_is_using_hashname(self):
        path = self.driver.put_file("documents", self.document)
        self.assertStartsWith(path, "documents/")
        self.assertEqual(FileSystem.extension(path), ".pdf")
        self.assertTrue(self.driver.exists(path))
        self.assertEqual(self.driver.get(path), "hello")

    def test_can_put_file_as_with_name(self):
        self.driver.put_file_as("documents", self.document, name="invoice_1")
        self.assertTrue(self.driver.exists("documents/invoice_1.pdf"))

    def test_can_put_file_as_with_filename(self):
        self.driver.put_file_as("documents", self.document, filename="invoice_1.txt")
        self.assertTrue(self.driver.exists("documents/invoice_1.txt"))

    def test_can_get_file(self):
        self.driver.put("key.log", "value")
        self.assertEqual(self.driver.get("key.log"), "value")
        self.assertTrue(self.driver.exists("key.log"))
        self.assertEqual(
            self.driver.get_path("key.log"),
            os.path.join(base_path(self.get_root()), "key.log"),
        )

    def test_can_check_file_exists(self):
        self.driver.put("key.log", "value")
        self.assertTrue(self.driver.exists("key.log"))
        self.assertFalse(self.driver.exists("other_key.log"))
        self.assertFalse(self.driver.exists("other/key.log"))

    def test_can_check_file_missing(self):
        self.driver.put("key.log", "value")
        self.assertTrue(self.driver.missing("other_key.log"))
        self.assertFalse(self.driver.missing("key.log"))
        self.assertTrue(self.driver.missing("other/key.log"))

    # def test_can_stream(self):
    #     self.driver.put("key.log", "value")
    #     stream = self.driver.stream("key.log")
    #     self.assertEqual(stream.name(), "key.log")
    #     self.assertEqual(stream.extension(), ".log")

    def test_can_get_size(self):
        path = self.driver.put("doc.pdf", "hello")
        path2 = self.driver.put("doc2.pdf", "hello I am bigger !")
        self.assertGreater(self.driver.size("doc.pdf"), 0)
        self.assertGreater(self.driver.size("doc2.pdf"), self.driver.size("doc.pdf"))

    def test_can_get_human_size(self):
        path = self.driver.put("doc.pdf", "hello")
        self.assertTrue(self.driver.human_size("doc.pdf"), "5 bytes")

    def test_can_get_last_modified(self):
        path = self.driver.put("doc.pdf", "hi")
        last_modified = self.driver.last_modified("doc.pdf")
        path = self.driver.append("doc.pdf", "sam")
        self.assertGreater(self.driver.last_modified("doc.pdf"), last_modified)

    # def test_can_move_files(self):
    #     # TODO: ensure directories are created along moving file...
    #     self.driver.put("key.log", "value")
    #     self.driver.move("key.log", "logs/key.log")
    #     self.assertTrue(self.driver.missing("key.log"))
    #     self.assertTrue(self.driver.exists("key.log"))
    #     self.assertTrue(self.driver.get("logs/key.log"), "value")

    def test_can_copy_files(self):
        self.driver.put("key.log", "value")
        self.driver.copy("key.log", "other_key.log")
        self.assertTrue(self.driver.exists("key.log"))
        self.assertEqual(self.driver.get("other_key.log"), "value")

    def test_can_delete_files(self):
        self.driver.put("delete.log", "value")
        self.driver.delete("delete.log")
        self.assertFalse(self.driver.exists("delete.log"))

    def test_can_prepend_file(self):
        self.driver.put("world.log", "world")
        self.driver.prepend("world.log", "Hello ")
        self.assertTrue(self.driver.get("world.log"), "Hello world")

    def test_can_prepend_empty_file(self):
        self.driver.put("world.log", "")
        self.driver.prepend("world.log", "Hello")
        self.assertTrue(self.driver.get("world.log"), "Hello")

    def test_can_prepend_non_existing_file(self):
        self.driver.prepend("world.log", "Hello")
        self.assertTrue(self.driver.get("world.log"), "Hello")

    def test_can_append_file(self):
        self.driver.put("world.log", "Hello")
        self.driver.append("world.log", " world")
        self.assertTrue(self.driver.get("world.log"), "Hello world")

    def test_can_append_empty_file(self):
        self.driver.put("world.log", "")
        self.driver.append("world.log", "Hello")
        self.assertTrue(self.driver.get("world.log"), "Hello")

    def test_can_append_non_existing_file(self):
        self.driver.append("world.log", "Hello")
        self.assertTrue(self.driver.get("world.log"), "Hello")

    def test_get_name(self):
        name = self.driver.get_name("some_file.txt", "log")
        self.assertEqual(name, "log.txt")

        name = self.driver.get_name("some_file.tar.gz", "archive")
        self.assertEqual(name, "archive.tar.gz")

        name = self.driver.get_name("path/to/some/file.png")
        self.assertEqual(name, "file.png")

    def test_can_get_files_in_directory(self):
        self.assertLen(self.driver.files(), 0)

        # root by default
        self.driver.put("key.log", "")
        self.driver.put("image.png", "")
        self.driver.put(".hidden", "")
        self.driver.put("docs/1.pdf", "")

        self.assertEqual(
            self.driver.files().pluck("filename"), [".hidden", "image.png", "key.log"]
        )
        # subdirectory if given
        self.assertEqual(self.driver.files("docs/").pluck("filename"), ["1.pdf"])
        self.assertEqual(self.driver.files("docs").pluck("filename"), ["1.pdf"])

    def test_can_get_all_files_in_directory(self):
        self.assertLen(self.driver.all_files(), 0)

        # root by default
        self.driver.put("key.log", "")
        self.driver.put("image.png", "")
        self.driver.put(".hidden", "")
        self.driver.put("docs/1.pdf", "")
        self.driver.put("docs/private/invoice.pdf", "")
        self.assertEqual(
            self.driver.all_files().pluck("filename"),
            [".hidden", "1.pdf", "image.png", "invoice.pdf", "key.log"],
        )
        # subdirectory if given
        self.assertEqual(
            self.driver.all_files("docs").pluck("filename"), ["1.pdf", "invoice.pdf"]
        )
        self.assertEqual(
            self.driver.all_files("docs/private").pluck("filename"), ["invoice.pdf"]
        )

    def test_can_get_directories(self):
        self.assertLen(self.driver.directories(), 0)

        # root by default
        self.driver.put("key.log", "")
        self.driver.put("docs/1.pdf", "")
        self.driver.put("docs/private/invoice.pdf", "")
        self.assertEqual(
            self.driver.directories(),
            ["docs"],
        )

    def test_can_get_url(self):
        self.driver.put("logs/world.log", "hello")
        url = self.driver.get_url("logs/world.log")
        self.assertEqual(url, "/storage/logs/world.log")

        self.driver.put("public/avatar.png", "hello")
        url = self.driver.get_url("public/avatar.png")
        self.assertEqual(url, "/storage/avatar.png")
