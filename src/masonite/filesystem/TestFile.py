from .UploadedFile import UploadedFile
import tempfile
from ..utils.filesystem import mimetypes


class TestFile(UploadedFile):
    def __init__(self, filename, mimetype, content):
        super().__init__(filename, mimetype, content)
        self.temp_file = None
        self.fake_mimetype = mimetype
        self.fake_size = len(self.get_content())

    @classmethod
    def create(
        cls, path: str, size: int = None, mimetype: str = None, temporary: bool = True
    ):
        fp = tempfile.NamedTemporaryFile(suffix=path, delete=temporary)
        if size:
            fp.truncate(size)
            fp.seek(0)
        if not mimetype:
            mimetype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        file = cls(path, mimetype, fp.read())
        file.temp_file = fp
        return file

    @classmethod
    def image(
        cls, path: str, width: int = 100, height: int = 100, temporary: bool = True
    ):
        from PIL import Image

        fp = tempfile.NamedTemporaryFile(suffix=path, delete=temporary)
        img = Image.new("RGB", (width, height), "#FF0000")
        img.save(fp)
        fp.seek(0)
        mimetype = mimetypes.guess_type(path)[0] or "image/*"
        file = cls(path, mimetype, fp.read())
        file.temp_file = fp
        return file

    def size(self, size):
        self.fake_size = size
        return self

    def mimetype(self, mimetype):
        self.fake_mimetype = mimetype
        return self

    def get_size(self) -> int:
        return self.fake_size

    def get_mimetype(self):
        return self.fake_mimetype

    def get_original_mimetype(self):
        return self.fake_mimetype

    def get_extension(self, without_dot=False):
        return self.get_original_extension(without_dot)

    def get_path(self):
        return self.temp_file.name
