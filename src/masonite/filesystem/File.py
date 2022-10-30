import magic
import os
import uuid

from ..utils.filesystem import FileSystem
from ..facades import Storage


class File:
    """High-level class to manipulate a file."""

    def __init__(self, path: str, content=None):
        self.path = path
        self._content = content

        self._hashname = None

    def __repr__(self):
        return f"{self.__class__.__name__}(filename={self.filename})"

    def get_content(self):
        if self._content:
            return self._content
        else:
            return FileSystem.get(self.path)

    def get_extension(self, without_dot=False):
        """Get extension from mime type. If the mime type is unknown it returns None."""
        extension_without_dot = magic.Magic(extension=True).from_file(self.path)
        if extension_without_dot == "???":
            return None
        if without_dot:
            return extension_without_dot
        else:
            return "." + extension_without_dot

    def get_mimetype(self):
        """Get MIME Type from content."""
        return magic.from_file(self.path, mime=True)

    def guess_extension(self, without_dot=False):
        """Guess extension from path. Be careful that is unsafe and can be tampered with."""
        return FileSystem.extension(self.path, without_dot)

    @property
    def extension(self):
        """If no extension found from mime type, fallback to extension computed from path."""
        return self.get_extension() or self.guess_extension()

    @property
    def mimetype(self):
        return self.get_mimetype()

    @property
    def name(self):
        return FileSystem.filename(self.path)

    @property
    def filename(self):
        return FileSystem.basename(self.path)

    def get_infos(self):
        return {
            "filename": self.filename,
            "extension": self.extension,
            "mimetype": self.mimetype,
            "original_extension": self.get_original_extension(),
            "original_mimetype": self.get_original_mimetype(),
            "size": self.size,
            "human_size": self.get_human_size(),
        }

    def get_size(self) -> int:
        """Get file size in bytes."""
        return FileSystem.size(self.path)

    def get_human_size(self) -> str:
        """Get file size represented as a human readable size string."""
        return FileSystem.human_size(self.path)

    @property
    def size(self):
        return self.get_size()

    def file_hash(self, algorithm="md5"):
        """Return unique hash representing file content. Default hashing algorithm is md5."""
        hash_string = FileSystem.hash(self.get_content(), algorithm)
        return f"{hash_string}{self.extension}"

    def hash_path(self):
        return os.path.join(FileSystem.dirname(self.path), self.hash_name())

    def hash_name(self):
        if not self._hashname:
            self._hashname = f"{str(uuid.uuid4())}{self.extension}"
        return self._hashname

    def stream(self):
        return self.get_content()

    def store(self, path: str, disk: str = "default"):
        relative_path = Storage.disk(disk).put_file(path, self)
        return relative_path

    def store_as(self, path: str, name: str = "", filename: str = "", disk="default"):
        relative_path = Storage.disk(disk).put_file_as(
            path, self, name=name, filename=filename
        )
        return relative_path
