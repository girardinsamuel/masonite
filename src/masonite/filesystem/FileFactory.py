import tempfile


class FileFactory:
    def __init__(self) -> None:
        pass

    def create(self, path, size, temporary=False):
        # # fp = tempfile.TemporaryFile()
        # fp = tempfile.NamedTemporaryFile(prefix=path, suffix="avatar.png")
        # fp.seek()
        # size_in_bytes = size
        # fp.seek(size_in_bytes - 1)
        # fp.write("\0")
        # return fp

    def image(self, path, height, width):
        pass
