from tests import TestCase
from src.masonite.facades import Storage
from src.masonite.filesystem.TestFile import TestFile


class TestMockStorage(TestCase):
    def setUp(self):
        super().setUp()
        self.fake("storage")

    def tearDown(self):
        super().tearDown()
        self.restore("storage")

    # def test_creating_test_file(self):
    #     doc = TestFile.create("document.pdf", 2048, "application/pdf")
    #     img = TestFile.image("image.png", 150, 150)

    def test_saving_test_file(self):
        doc = TestFile.create("document.pdf", 2048)
        doc.store("invoices", "local")
        Storage.assertExists(f"invoices/{doc.hash_name()}", "local")

        Storage.flush("local")
        import pdb

        pdb.set_trace()
        Storage.disk("local").put_file("invoices", doc)
        Storage.assertExists(f"invoices/{doc.hash_name()}", "local")

    def test_saving_file(self):

        Storage.disk("s3").put("test.txt", "hello")
        Storage.disk("local").put("test2.txt", "hello")
        Storage.disk("s3").put("test2.txt", "hello")

        Storage.assertExists("test.txt", "s3")
        Storage.assertMissing("hello.txt", "s3")
