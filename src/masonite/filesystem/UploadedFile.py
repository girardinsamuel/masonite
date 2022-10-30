import magic

from ..utils.filesystem import FileSystem, mimetypes
from . import File


class UploadedFile(File):
    """High-level class to manipulate an uploaded file coming from an HTTP request."""

    def __init__(self, path: str, content=None, original_mimetype: str = None):
        super().__init__(path, content)
        self._original_filename = path
        self._original_mimetype = original_mimetype

    def get_content(self):
        return self._content

    def get_extension(self, without_dot=False):
        """Guess extension from mime type."""
        extension_without_dot = magic.Magic(extension=True).from_buffer(
            self.get_content()
        )
        if extension_without_dot == "???":
            return None

        if without_dot:
            return extension_without_dot
        else:
            return "." + extension_without_dot

    def get_original_extension(self, without_dot=False):
        """Get extension from path (can be tampered with -> unsafe)."""
        return FileSystem.extension(self._original_filename, without_dot)

    def get_mimetype(self):
        """Get MIME Type from content."""
        return magic.from_buffer(self.get_content(), mime=True)

    def get_original_mimetype(self):
        """Get MIME Type from path (can be tampered with -> unsafe)."""
        return self._original_mimetype or mimetypes.guess_type(self.filename)[0]

    def get_original_filename(self):
        return self._original_filename

    def get_size(self) -> int:
        """Get file size in bytes."""
        return len(self._content)

    def get_human_size(self) -> str:
        """Get file size represented as a human readable size string."""
        from hfilesize import FileSize

        return FileSize(self.get_size()).format()

    def hash_path(self):
        """Has no path"""
        return self.hash_name()
