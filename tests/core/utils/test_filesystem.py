import os
from tests import TestCase
from src.masonite.tests import TestFilesAndDirs
from src.masonite.utils.filesystem import FileSystem


class TestFileSystem(TestCase, TestFilesAndDirs):
    def create_file(self, path: str, content: str = "") -> str:
        filepath = self.get_path(path)
        with open(filepath, "w") as f:
            content = f.write(content)
        return filepath

    def create_dir(self, path: str) -> str:
        dirpath = self.get_path(path)
        os.makedirs(dirpath, exist_ok=True)
        return dirpath

    def test_exists(self):
        assert not FileSystem.exists("unknown.pdf")
        assert not FileSystem.exists("unknown/path/")

        # for file
        path = self.create_file("doc.pdf")
        assert FileSystem.exists(path)

        # for directory
        path = self.create_dir("docs/")
        assert FileSystem.exists(path)

    def test_missing(self):
        assert FileSystem.missing("unknown.pdf")
        assert FileSystem.missing("unknown/path/")

        # for file
        path = self.create_file("doc.pdf")
        assert not FileSystem.missing(path)

        # for directory
        path = self.create_dir("docs/")
        assert not FileSystem.missing(path)

    def test_make_directory(self):
        path = self.get_path("test")
        FileSystem.make_directory(path)
        assert FileSystem.exists(path)
        assert FileSystem.is_directory(path)

    def test_file_exists(self):
        assert not FileSystem.file_exists("unknown.pdf")

        path = self.create_file("doc.pdf")
        assert FileSystem.file_exists(path)

        path = self.create_dir("docs/")
        assert not FileSystem.file_exists(path)

    def test_file_missing(self):
        assert FileSystem.file_missing("unknown.pdf")

        path = self.create_file("doc.pdf")
        assert not FileSystem.file_missing(path)

    def test_is_file(self):
        assert not FileSystem.is_file("unknown.pdf")

        path = self.create_file("doc.pdf")
        assert FileSystem.is_file(path)

        path = self.create_dir("docs/")
        assert not FileSystem.is_file(path)

    def test_is_directory(self):
        assert not FileSystem.is_directory("unknown/path")

        path = self.create_dir("docs/")
        assert FileSystem.is_directory(path)

        path = self.create_file("doc.pdf")
        assert not FileSystem.is_directory(path)

    def test_is_empty_directory(self):
        path = self.create_dir("docs/")
        assert FileSystem.is_empty_directory(path)

        path = self.create_file("docs/doc.pdf")
        assert not FileSystem.is_empty_directory(path)

    def test_get(self):
        with self.assertRaises(Exception):
            FileSystem.get("unknown.pdf")

        path = self.create_file("doc.pdf", "hello")
        assert FileSystem.get(path) == "hello"

    def test_created(self):
        path = self.create_file("doc.pdf")

        assert FileSystem.created(path) == FileSystem.last_modified(path)
        assert FileSystem.created(path)
        assert float(FileSystem.created(path))

    def test_last_modified(self):
        path = self.create_file("doc.pdf")
        last_modified = FileSystem.last_modified(path)
        assert last_modified
        assert float(last_modified)
        # make modification to file
        FileSystem.append(path, "hello")
        assert FileSystem.last_modified(path) > last_modified

    def test_extension(self):
        self.assertEqual(FileSystem.extension("log.txt"), ".txt")
        self.assertEqual(FileSystem.extension("archive.tar.gz"), ".tar.gz")
        self.assertEqual(FileSystem.extension("path/to/log.txt"), ".txt")
        self.assertEqual(FileSystem.extension("image.iso"), ".iso")
        self.assertEqual(
            FileSystem.extension("archlinux-2022.09.03-x86_64.iso"), ".iso"
        )
        self.assertEqual(FileSystem.extension(".hidden_file"), "")
        self.assertEqual(FileSystem.extension("file-without-extension"), "")

        self.assertEqual(FileSystem.extension("log.txt", without_dot=True), "txt")
        self.assertEqual(
            FileSystem.extension("archive.tar.gz", without_dot=True), "tar.gz"
        )
        self.assertEqual(FileSystem.extension(".hidden_file", without_dot=True), "")
        self.assertEqual(
            FileSystem.extension("file-without-extension", without_dot=True), ""
        )

    def test_basename(self):
        assert FileSystem.basename("test/path/file.pdf") == "file.pdf"

    def test_filename(self):
        assert FileSystem.filename("test/path/file.pdf") == "file"

    def test_dirname(self):
        assert FileSystem.dirname("test/path/file.pdf") == "test/path"
        assert FileSystem.dirname("test/path") == "test"
        assert FileSystem.dirname("test/path/") == "test"

    def test_is_readable(self):
        # if does not exist
        assert not FileSystem.is_readable("test/path/file.pdf")
        # or if no read permissions
        path = self.create_file("doc.pdf")
        FileSystem.chmod(path, "000")
        assert not FileSystem.is_readable(path)

        # or if has read permissions
        FileSystem.chmod(path, "444")
        assert FileSystem.is_readable(path)

    def test_is_writable(self):
        # if does not exist
        assert not FileSystem.is_writable("test/path/file.pdf")
        # or if no write permissions
        path = self.create_file("doc.pdf")
        FileSystem.chmod(path, "000")
        assert not FileSystem.is_writable(path)

        # or if has write permissions
        FileSystem.chmod(path, "222")
        assert FileSystem.is_writable(path)

    def test_glob(self):
        self.create_file("doc1.pdf")
        self.create_file("img.png")
        self.create_file(".hidden")
        self.create_dir("docs/")
        self.create_file("docs/avatar.pdf")

        # everything recursively
        files = []
        for file in FileSystem.glob(self.get_path("**/*")):
            files.append(file)
        assert len(files) == 5

        # only pdfs recursively
        files = []
        for file in FileSystem.glob(self.get_path("**/*.pdf")):
            files.append(file)
        assert len(files) == 2

        # only pngs recursively
        files = []
        for file in FileSystem.glob(self.get_path("**/*.png")):
            files.append(file)
        assert len(files) == 1

        # only at root (three files and one folder)
        files = []
        for file in FileSystem.glob(self.get_path("*")):
            files.append(file)
        assert len(files) == 4

    def test_files(self):
        # at root, no files
        assert len(FileSystem.files(self.get_path())) == 0

        self.create_file("doc1.pdf")
        self.create_file("img.png")
        self.create_file(".hidden")
        self.create_dir("docs/")
        self.create_file("docs/avatar.pdf")

        assert FileSystem.files(self.get_path()) == [".hidden", "doc1.pdf", "img.png"]
        assert FileSystem.files(self.get_path("docs")) == ["avatar.pdf"]

    def test_all_files(self):
        # at root, no files
        assert len(FileSystem.all_files(self.get_path())) == 0

        self.create_file("doc1.pdf")
        self.create_file("img.png")
        self.create_file(".hidden")
        self.create_dir("docs/")
        self.create_file("docs/avatar.pdf")

        assert len(FileSystem.all_files(self.get_path())) == 4
        assert FileSystem.all_files(self.get_path("docs")) == ["avatar.pdf"]

    def test_directories(self):
        # at root, no files
        assert len(FileSystem.directories(self.get_path())) == 0
        self.create_file("doc.pdf")
        self.create_dir("images/")
        self.create_file("images/image.png")
        self.create_dir("docs/")
        self.create_dir("docs/private/")

        assert FileSystem.directories(self.get_path()) == ["docs", "images"]
        assert FileSystem.directories(self.get_path("docs")) == ["private"]

    def test_hash(self):
        path = self.create_file("doc.pdf", "hello")
        hash_string = FileSystem.hash(path)
        assert len(hash_string) > 0

        other_path = self.create_file("doc2.pdf", "hello")
        assert hash_string == FileSystem.hash(other_path)

    def test_providing_wrong_hash_algorithm_raises_exception(self):
        path = self.create_file("doc.pdf", "hello")
        with self.assertRaises(Exception) as context:
            hash_string = FileSystem.hash(path, "unknown_md5")
        assert str(context.exception).startswith("Unsupported hashing algorithm")

    def test_can_change_hash_algorithm(self):
        path = self.create_file("doc.pdf")
        sha1_hash = FileSystem.hash(path, "sha1")
        md5_hash = FileSystem.hash(path, "md5")
        assert sha1_hash != md5_hash

    def test_has_same_hash(self):
        path = self.create_file("doc.pdf", "hi")
        path2 = self.create_file("doc2.pdf", "hi")

        assert FileSystem.has_same_hash(path, path2)

        path3 = self.create_file("doc3.pdf", "ho")
        assert not FileSystem.has_same_hash(path, path3)

    def test_put(self):
        path = self.get_path("doc.pdf")
        FileSystem.put(path, "hello")

        # creates if does not exist
        assert FileSystem.exists(path)
        assert FileSystem.get(path) == "hello"

        # overrides if exists already
        FileSystem.put(path, "hi")
        assert FileSystem.get(path) == "hi"

    def test_put_accepts_bytes(self):
        path = self.get_path("doc.pdf")
        FileSystem.put(path, b"hello")
        assert FileSystem.get(path) == "hello"

    def test_replace(self):
        path = self.get_path("doc.pdf")
        FileSystem.replace(path, "hello")

        # creates if does not exist
        assert FileSystem.exists(path)
        assert FileSystem.get(path) == "hello"

        # overrides if exists already
        FileSystem.replace(path, "hi")
        assert FileSystem.get(path) == "hi"

    def test_replace_in_file(self):
        path = self.create_file("doc.txt", "hello there ! hello again. hello")
        FileSystem.replace_in_file(path, "hello", "hi")
        assert FileSystem.get(path) == "hi there ! hi again. hi"

        # replace only two occurrences
        path = self.create_file("doc2.txt", "hello there ! hello again. hello")
        FileSystem.replace_in_file(path, "hello", "hi", 2)
        assert FileSystem.get(path) == "hi there ! hi again. hello"

    def test_prepend_on_non_existing_file(self):
        path = self.get_path("doc.pdf")
        FileSystem.prepend(path, "hello")
        assert FileSystem.get(path) == "hello"

    def test_prepend(self):
        path = self.create_file("doc.pdf", "world")
        FileSystem.prepend(path, "hello ")
        assert FileSystem.get(path) == "hello world"

    def test_chmod_can_get_chmod_as_string_of_ints(self):
        path = self.create_file("doc.pdf")
        assert FileSystem.chmod(path) == "644"

    def test_chmod_can_set_chmod(self):
        path = self.create_file("doc.pdf")

        FileSystem.chmod(path, "777")
        assert FileSystem.chmod(path) == "777"

    def test_strchmod(self):
        path = self.create_file("doc.pdf")
        assert FileSystem.strchmod(path) == "-rw-r--r--"

    def test_delete(self):
        assert not FileSystem.delete("test/path/unknown.pdf")
        path = self.create_file("doc.pdf")
        assert FileSystem.delete(path)

        path = self.create_dir("docs/")
        with self.assertRaises(Exception):
            FileSystem.delete(path)

    def test_move(self):
        path = self.create_file("doc.pdf")
        new_path = self.get_path("doc2.pdf")
        FileSystem.move(path, new_path)
        assert not FileSystem.exists(path)
        assert FileSystem.is_file(new_path)

    def test_copy(self):
        path = self.create_file("doc.pdf", "hi")
        new_path = self.get_path("doc2.pdf")
        FileSystem.copy(path, new_path)
        assert FileSystem.exists(path)
        assert FileSystem.is_file(new_path)
        assert FileSystem.get(new_path) == "hi"

    def test_copy_cannot_copy_directory(self):
        path = self.create_dir("docs/")
        new_path = self.get_path("documents/")

        with self.assertRaises(IsADirectoryError):
            FileSystem.copy(path, new_path)

    def test_make_directory(self):
        path = self.get_path("docs/")
        assert FileSystem.make_directory(path)
        assert FileSystem.is_directory(path)
        assert FileSystem.chmod(path) == "755"

        path = self.get_path("images/")
        assert FileSystem.make_directory(path, recursive=False)
        assert FileSystem.is_directory(path)
        assert FileSystem.chmod(path) == "755"

    def test_can_specify_mode_with_make_directory(self):
        path = self.get_path("docs/")
        assert FileSystem.make_directory(path, "777")
        assert FileSystem.is_directory(path)
        assert FileSystem.chmod(path) == "777"

    def test_make_directory_recursively(self):
        path = self.get_path("private/docs/users/1")
        assert FileSystem.make_directory(path)
        assert FileSystem.is_directory(self.get_path("private"))
        assert FileSystem.is_directory(self.get_path("private/docs"))
        assert FileSystem.is_directory(self.get_path("private/docs/users"))
        assert FileSystem.is_directory(path)

    def test_make_directory_with_existing_directory_must_be_forced(self):
        self.create_dir("private/users/")
        path = self.get_path("private/users/")
        assert not FileSystem.make_directory(path)

        # needs to be forced
        assert FileSystem.make_directory(path, force=True)
        assert FileSystem.is_directory(path)

    def test_can_disable_recursive_mode_when_making_directory(self):
        path = self.get_path("private/docs/users/1")
        with self.assertRaises(FileNotFoundError):
            FileSystem.make_directory(path, recursive=False)

    def test_ensure_directory_exists(self):
        path = self.get_path("private/docs/users/1")
        assert not FileSystem.is_directory(path)

        FileSystem.ensure_directory_exists(path)
        assert FileSystem.is_directory(path)
        assert FileSystem.chmod(path) == "755"

    def test_delete_directory(self):
        assert not FileSystem.delete_directory("unknown.pdf")
        assert not FileSystem.delete_directory("unknown/docs/")
        path = self.create_file("doc.pdf")
        assert not FileSystem.delete_directory(path)

        path = self.create_dir("docs/")
        assert FileSystem.delete_directory(path)
        assert not FileSystem.exists(path)

        path = self.create_dir("docs/")
        self.create_file("docs/test.pdf")
        assert FileSystem.delete_directory(path, preserve=True)
        assert FileSystem.exists(path)
        assert FileSystem.is_empty_directory(path)

    def test_copy_directory_to_unexisting_destination(self):
        path = self.create_dir("docs/")
        destination = self.get_path("new_docs/")
        self.create_file("docs/img.png")
        self.create_file("docs/doc1.pdf")
        assert FileSystem.copy_directory(path, destination)
        assert FileSystem.is_directory(path)
        assert FileSystem.files(path) == ["doc1.pdf", "img.png"]
        assert FileSystem.is_directory(destination)
        assert FileSystem.files(destination) == ["doc1.pdf", "img.png"]

    def test_copy_directory_to_existing_destination(self):
        path = self.create_dir("docs/")
        destination = self.create_dir("new_docs/")
        self.create_file("docs/img.png")
        self.create_file("docs/doc1.pdf")
        with self.assertRaises(FileExistsError):
            FileSystem.copy_directory(path, destination)

        # must be forced
        assert FileSystem.copy_directory(path, destination, force=True)
        assert FileSystem.is_directory(path)
        assert FileSystem.files(path) == ["doc1.pdf", "img.png"]
        assert FileSystem.is_directory(destination)
        assert FileSystem.files(destination) == ["doc1.pdf", "img.png"]

    def test_move_directory(self):
        assert not FileSystem.move_directory("unkwown/path", "other/path")

        path = self.create_dir("docs/")
        self.create_file("docs/img.png")
        self.create_file("docs/doc1.pdf")
        destination = self.get_path("new_docs")
        assert FileSystem.move_directory(path, destination)
        assert not FileSystem.is_directory(path)
        assert FileSystem.is_directory(destination)
        assert FileSystem.files(destination) == ["doc1.pdf", "img.png"]

    def test_move_directory_to_existing_destination(self):
        path = self.create_dir("docs/")
        destination = self.create_dir("new_docs/")
        self.create_file("docs/img.png")
        self.create_file("docs/doc1.pdf")
        with self.assertRaises(FileExistsError):
            FileSystem.move_directory(path, destination)

        # must be forced
        assert FileSystem.move_directory(path, destination, force=True)
        assert not FileSystem.is_directory(path)
        assert FileSystem.is_directory(destination)
        assert FileSystem.files(destination) == ["doc1.pdf", "img.png"]

    def test_clean_directory(self):
        path = self.create_dir("docs/")
        self.create_file("docs/test.pdf")
        assert not FileSystem.is_empty_directory(path)
        FileSystem.clean_directory(path)

        assert FileSystem.exists(path)
        assert FileSystem.is_empty_directory(path)
