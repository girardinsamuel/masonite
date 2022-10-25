from typing import List
import os
import stat
import platform
import pathlib
import shutil
import hashlib
import mimetypes


def get_module_dir(module_file):
    return os.path.dirname(os.path.realpath(module_file))


def render_stub_file(stub_file, name):
    """Read stub file, replace placeholders and return content."""
    content = FileSystem.get(stub_file)
    content = content.replace("__class__", name)
    return content


mimetypes.init([os.path.join(get_module_dir(__file__), "data/mime.types")])

KNOWN_MIME_TYPES = mimetypes.types_map.keys()


class FileSystem:
    @staticmethod
    def exists(path: str) -> bool:
        """Check if a path exists (file or directory)."""
        return os.path.exists(path)

    @staticmethod
    def missing(path: str) -> bool:
        """Check if a path is missing (file or directory)."""
        return not FileSystem.exists(path)

    @staticmethod
    def file_exists(path: str) -> bool:
        """Check if a file path exists."""
        return FileSystem.is_file(path) and FileSystem.exists(path)

    @staticmethod
    def file_missing(path: str) -> bool:
        """Check if a file path is missing."""
        return not FileSystem.file_exists(path)

    @staticmethod
    def is_file(path: str) -> bool:
        """Check if path is a file."""
        return os.path.isfile(path)

    @staticmethod
    def is_directory(path: str) -> bool:
        """Check if path is a directory."""
        return os.path.isdir(path)

    @staticmethod
    def is_empty_directory(path: str) -> bool:
        """Check if path is an empty directory."""
        return os.path.isdir(path) and len(os.listdir(path)) == 0

    @staticmethod
    def get(path: str) -> str:
        """Get file contents at path."""
        if not FileSystem.is_file(path):
            raise Exception(f"File does not exist at path: {path}")

        with open(path, "r") as f:
            content = f.read()
        return content

    @staticmethod
    def created(path: str):
        """Try to get the date that a file was created, falling back to when it was
        last modified if that isn't possible.
        """
        if platform.system() == "Windows":
            return os.path.getctime(path)
        else:
            stat = os.stat(path)
            try:
                return stat.st_birthtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                # so we'll settle for when its content was last modified.
                return stat.st_mtime

    @staticmethod
    def last_modified(path):
        if platform.system() == "Windows":
            return os.path.getmtime(path)
        else:
            stat = os.stat(path)
            try:
                return stat.st_mtime
            except AttributeError:
                # We're probably on Linux. No easy way to get creation dates here,
                return 0

    @staticmethod
    def extension(filepath: str, without_dot=False) -> str:
        """Get file extension from a filepath. If without_dot=True the . prefix will be removed from
        the extension."""
        extension_parts = pathlib.Path(filepath).suffixes
        extension = ""
        if extension_parts:
            # try to join all the parts until only one part to check if it's a known extension
            for i in range(len(extension_parts)):
                try_extension = "".join(extension_parts[i:])
                if try_extension in KNOWN_MIME_TYPES:
                    extension = try_extension
                    break
            # if no known extension found, return the last part as the extension
            if not extension:
                extension = extension_parts[-1]

            if without_dot:
                extension = extension[1:]
        return extension

    @staticmethod
    def hash(path: str | bytes, algorithm: str = "md5") -> str:
        """Compute file hash with given algorithm from a content of a file."""
        try:
            hash_object = hashlib.new(algorithm)
        except ValueError:
            raise Exception(
                f"Unsupported hashing algorithm provided to 'get_hash()'. Available algorithms are: {hashlib.algorithms_available}."
            )
        if isinstance(path, str):
            with open(path, "rb") as f:
                # Read and update hash string value in blocks of 4K (this allow to read large files)
                for byte_block in iter(lambda: f.read(4096), b""):
                    hash_object.update(byte_block)
        else:
            hash_object.update(path)
        return hash_object.hexdigest()

    @staticmethod
    def has_same_hash(first_path: str, second_path: str) -> bool:
        return FileSystem.hash(first_path) == FileSystem.hash(second_path)

    @staticmethod
    def put(path: str, content: str | bytes) -> bool:
        """Write content to a file."""
        if isinstance(content, (bytes, bytearray)):
            mode = "wb"
        else:
            mode = "w"
        with open(path, mode) as f:
            f.write(content)
        return True

    @staticmethod
    def replace(path: str, content: str | bytes) -> bool:
        """Replace content of a file, overriding it if it exists."""
        # TODO: check if okay
        return FileSystem.put(path, content)

    @staticmethod
    def replace_in_file(path: str, search: str, replace: str, count=-1) -> bool:
        """Replace a searched string by an other in a file. The maximum number of
        occurrences to replace. -1 (the default value) means replace all occurrences."""
        content = FileSystem.get(path)
        return FileSystem.put(path, content.replace(search, replace, count))

    @staticmethod
    def prepend(path: str, content: str) -> bool:
        if FileSystem.file_exists(path):
            return FileSystem.put(path, content + FileSystem.get(path))

        return FileSystem.put(path, content)

    @staticmethod
    def append(path: str, content: str) -> bool:
        with open(path, "a") as f:
            f.write(content)
        return True

    @staticmethod
    def chmod(path: str, mode: str = None) -> str:
        """Get or set UNIX mode on file or directory."""
        if mode:
            octal_mode = int(str(mode), base=8)
            return os.chmod(path, octal_mode)

        return str(oct(os.stat(path).st_mode))[-3:]

    @staticmethod
    def strchmod(path: str) -> str:
        """Get UNIX mode on file or directory as a string representation with letters."""
        return stat.filemode(os.stat(path).st_mode)

    @staticmethod
    def delete(path: str) -> bool:
        """Remove the file at the given path."""
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def move(path: str, destination_path: str) -> bool:
        """Move file to a new location."""
        shutil.move(path, destination_path)

    @staticmethod
    def copy(path: str, destination_path: str) -> bool:
        """Copy file to a new location."""
        shutil.copyfile(path, destination_path)

    @staticmethod
    def basename(path: str) -> str:
        """Get file basename from a path (with extension)."""
        return os.path.basename(path)

    @staticmethod
    def filename(path: str) -> str:
        """Get file basename from a path (with extension)."""
        return os.path.splitext(FileSystem.basename(path))[0]

    @staticmethod
    def dirname(path: str) -> str:
        path = path.rstrip("/")
        return os.path.dirname(path)

    @staticmethod
    def is_readable(path: str) -> bool:
        """Check if file is readable."""
        return FileSystem.is_file(path) and os.access(path, os.R_OK)

    @staticmethod
    def is_writable(path: str) -> bool:
        """Check if file is writable."""
        return FileSystem.is_file(path) and os.access(path, os.W_OK)

    @staticmethod
    def glob(
        pattern: str,
    ):
        return pathlib.Path().glob(pattern)

    @staticmethod
    def files(directory: str) -> "List[str]":
        path = pathlib.Path(directory)
        _files = [FileSystem.basename(str(f)) for f in path.glob("*") if f.is_file()]
        _files.sort()
        return _files

    @staticmethod
    def all_files(directory: str) -> "List[str]":
        path = pathlib.Path(directory)
        _files = [FileSystem.basename(str(f)) for f in path.glob("**/*") if f.is_file()]
        _files.sort()
        return _files

    @staticmethod
    def directories(path: str) -> "List[str]":
        path = pathlib.Path(path)
        _dirs = [FileSystem.basename(str(f)) for f in path.glob("*") if f.is_dir()]
        _dirs.sort()
        return _dirs

    @staticmethod
    def make_directory(path: str, mode="755", force=False, recursive=True) -> bool:
        """Create a directory at the given path if it does not exist."""
        octal_mode = int(str(mode), base=8)
        try:
            if recursive:
                os.makedirs(path, octal_mode, exist_ok=force)
            else:
                os.mkdir(path, octal_mode)
            # ensure mode has correclty been set, sometimes mkdir or makedirs can have
            # issues with setting mode.
            if not FileSystem.chmod(path) == mode:
                FileSystem.chmod(path, mode)
            return True
        except FileExistsError:
            return False

    @staticmethod
    def ensure_directory_exists(path: str, mode="755", force=False) -> bool:
        """Ensure a directory at the given path exists, else create it."""
        if not FileSystem.is_directory(path):
            FileSystem.make_directory(path, mode, force)

    @staticmethod
    def move_directory(path: str, destination_path: str, force=False) -> bool:
        """Move a directory to a given destination."""
        result = FileSystem.copy_directory(path, destination_path, force)
        if result:
            FileSystem.delete_directory(path)
        return result

    @staticmethod
    def copy_directory(path: str, destination_path: str, force=False) -> bool:
        """Copy a directory to a given destination."""
        if not FileSystem.is_directory(path):
            return False
        shutil.copytree(path, destination_path, dirs_exist_ok=force)
        return True

    @staticmethod
    def delete_directory(path: str, preserve=False) -> bool:
        """Delete a directory."""
        if not FileSystem.is_directory(path):
            return False
        previous_mode = FileSystem.chmod(path)
        shutil.rmtree(path)

        if preserve:
            FileSystem.make_directory(path, previous_mode, force=True)
        return True

    @staticmethod
    def clean_directory(path: str) -> bool:
        """Clean a directory."""
        return FileSystem.delete_directory(path, True)
