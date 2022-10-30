import os
from typing import List

from ..FileStream import FileStream
from ..File import File
from ..UploadedFile import UploadedFile
from ...utils.filesystem import FileSystem
from ...utils.collections import Collection, collect


class LocalDriver:
    def __init__(self, application):
        self.application = application
        self.options = {}

    def set_options(self, options):
        self.options = options
        return self

    def get_path(self, path: str) -> str:
        """Get absolute path to given path in this locale driver."""
        abs_path = os.path.join(self.options.get("path"), path)
        return abs_path

    def get_name(self, path: str, alias: str = None):
        """
        /path/to/avatar.jpg -> avatar.jpg
        /path/to/avatar.jpg, photo -> photo.jpg
        """
        extension = FileSystem.extension(path)
        filename = FileSystem.filename(path)
        if alias:
            filename = alias
        return f"{filename}{extension}"

    def size(self, path: str) -> int:
        return FileSystem.size(self.get_path(path))

    def human_size(self, path: str) -> str:
        return FileSystem.human_size(self.get_path(path))

    def last_modified(self, path: str) -> float:
        return FileSystem.last_modified(self.get_path(path))

    def put(self, path: str, content: str | bytes | bytearray) -> bool:
        abs_path = self.get_path(path)
        FileSystem.ensure_directory_exists(FileSystem.dirname(abs_path))
        return FileSystem.put(abs_path, content)

    def put_file(self, path: str, file: File | UploadedFile) -> str:
        relative_filepath = os.path.join(path, file.hash_name())
        self.put(relative_filepath, file.get_content())
        return relative_filepath

    def put_file_as(
        self, path: str, file: UploadedFile, name: str = "", filename: str = ""
    ) -> str:
        if name:
            filename = f"{name}{file.extension}"
        elif filename:
            pass
        else:
            raise Exception(
                "You must provide a name/filename when using put_file_as()."
            )
        relative_filepath = os.path.join(path, filename)
        self.put(relative_filepath, file.get_content())
        return relative_filepath

    def get(self, path: str) -> "str|None":
        try:
            return FileSystem.get(self.get_path(path))
        except FileNotFoundError:
            return None

    def exists(self, path: str) -> bool:
        return FileSystem.exists(self.get_path(path))

    def missing(self, path: str) -> bool:
        return FileSystem.missing(self.get_path(path))

    def stream(self, path: str) -> FileStream:
        content = self.get(self.get_path(path))
        return FileStream(content, self.get_path(path))

    def copy(self, src: str, destination: str) -> bool:
        src_path = self.get_path(src)
        destination_path = self.get_path(destination)
        return FileSystem.copy(src_path, destination_path)

    def move(self, src: str, destination: str) -> bool:
        src_path = self.get_path(src)
        destination_path = self.get_path(destination)
        return FileSystem.move(src_path, destination_path)

    def prepend(self, path: str, content: str) -> bool:
        return FileSystem.prepend(self.get_path(path), content)

    def append(self, path: str, content: str) -> bool:
        return FileSystem.append(self.get_path(path), content)

    def delete(self, path: str) -> bool:
        return FileSystem.delete(self.get_path(path))

    def make_directory(
        self, directory_path: str, mode="755", force=False, recursive=True
    ):
        return FileSystem.make_directory(
            self.get_path(directory_path), mode, force, recursive
        )

    def delete_directory(self, directory_path: str, preserve: bool = False) -> bool:
        return FileSystem.delete_directory(self.get_path(directory_path), preserve)

    def files(self, directory_path: str = "") -> "Collection[File]":
        filepaths = collect(FileSystem.files(self.get_path(directory_path)))
        # return filepaths.map_into(File)
        return filepaths.map_into(
            lambda filename: File(
                os.path.join(
                    self.get_path(directory_path),
                    filename,
                )
            )
        )

    def all_files(self, directory_path: str = "") -> "Collection[File]":
        filepaths = collect(FileSystem.all_files(self.get_path(directory_path)))
        return filepaths.map_into(File)

    def directories(self, directory_path: str = "") -> "Collection[str]":
        return collect(FileSystem.directories(self.get_path(directory_path)))

    def get_url(self, path: str):
        path = os.path.join("/storage", path)

        if "/storage/public" in path:
            path = path.replace("/public", "", 1)

        return path
