import magic
import os

from ..utils.filesystem import FileSystem, mimetypes
from ..facades import Storage


class UploadedFile:
    def __init__(self, filename, mimetype, content):
        self._original_filename = filename
        self._original_mimetype = mimetype
        self._content = content

        self._filename = filename

    def get_extension(self, without_dot=False):
        """Guess extension from mime type."""
        extension_without_dot = magic.Magic(extension=True).from_buffer(
            self.get_content()
        )
        if without_dot:
            return extension_without_dot
        else:
            return "." + extension_without_dot

    def get_original_extension(self, without_dot=False):
        """Get extension from path (can be tampered with -> unsafe)."""
        return FileSystem.extension(self.filename, without_dot)

    def get_mimetype(self):
        """Get MIME Type from content."""
        return magic.from_buffer(self.get_content(), mime=True)

    def get_original_mimetype(self):
        """Get MIME Type from path (can be tampered with -> unsafe)."""
        return self._original_mimetype or mimetypes.guess_type(self.filename)[0]

    def get_original_filename(self):
        return self._original_filename

    def get_name(self):
        return os.path.splitext(self.filename)[0]

    def get_filename(self):
        """with extension."""
        return self._filename

    def get_infos(self):
        return {
            "filename": self.filename,
            "extension": self.get_extension(),
            "mimetype": self.get_mimetype(),
            "original_extension": self.get_original_extension(),
            "original_mimetype": self.get_original_mimetype(),
            "size": self.get_size(),
            "human_size": self.get_human_size(),
            "hash": self.hash_name(),
        }

    @property
    def name(self):
        return self.get_name()

    @property
    def filename(self):
        return self.get_filename()

    def get_size(self) -> int:
        """Get file size in bytes."""
        return len(self._content)

    def get_human_size(self) -> str:
        """Get file size represented as a human readable size string."""
        from hfilesize import FileSize

        return FileSize(self.get_size()).format()

    @property
    def size(self):
        return self.get_size()

    def get_content(self):
        return self._content

    def hash_name(self, algorithm="md5"):
        """Return unique hashed name with extension."""
        hash_string = FileSystem.hash(self.get_content(), algorithm)
        return hash_string + self.get_extension()

    def get_path(self):
        """An uploaded file does not have a path yet, so return only the filename."""
        return self.get_filename()

    def stream(self):
        return self.get_content()

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.get_filename()})"

    def store(self, path, disk="default"):
        relative_path = Storage.disk(disk).put_file(path, self, name=self.hash_name())
        return relative_path

    def store_as(self, path, name, disk="default"):
        relative_path = Storage.disk(disk).put_file(path, self, name=name)
        return relative_path
