from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..foundation import Application


class Storage:
    """File storage manager for Masonite handling managing files with different drivers."""

    def __init__(self, application: "Application", store_config: dict = None):
        self.application = application
        self.drivers = {}
        self.store_config = store_config or {}
        self.options = {}

    def add_driver(self, name: str, driver: str):
        self.drivers.update({name: driver})

    def set_configuration(self, config: dict) -> "Storage":
        self.store_config = config
        return self

    def get_driver(self, name: str = None) -> Any:
        if name is None:
            return self.drivers[self.store_config.get("default")]
        return self.drivers[name]

    def get_config_options(self, name: str = None) -> dict:
        if name is None or name == "default":
            return self.store_config.get(self.store_config.get("default"))

        return self.store_config.get(name)

    # Public API below
    def disk(self, name: str = "default") -> Any:
        """Get the file manager instance for the given disk name."""
        store_config = self.get_config_options(name)
        driver = self.get_driver(self.get_config_options(name).get("driver"))
        return driver.set_options(store_config)

    # TODO: add typing contract of storage driver
    def build(self, driver_name: str, options: dict = {}) -> Any:
        """Get a storage driver instance based on the given driver built on the fly with the given options."""
        driver = self.get_driver(driver_name)
        return driver.set_options(options)

    def get_path(self, path: str) -> str:
        """Get absolute path to given path for default driver."""
        return self.disk("default").get_path(path)

    def get_name(self, path: str, alias: str = None):
        return self.disk("default").get_name(path, alias)

    def size(self, path: str) -> int:
        return self.disk("default").size(path)

    def human_size(self, path: str) -> str:
        return self.disk("default").human_size(path)

    def last_modified(self, path: str) -> float:
        return self.disk("default").last_modified(path)

    def put(self, path: str, content: str | bytes | bytearray):
        return self.disk("default").put(path, content)

    def put_file(self, path: str, file: File | UploadedFile):
        return self.disk("default").put_file(path, file)

    def put_file_as(
        self, path: str, file: UploadedFile, name: str = "", filename: str = ""
    ):
        return self.disk("default").put_file_as(path, file, name, filename)

    def get(self, path: str) -> "str|None":
        return self.disk("default").get(path)

    def exists(self, path: str) -> bool:
        return self.disk("default").exists(path)

    def missing(self, path: str) -> bool:
        return self.disk("default").missing(path)

    def stream(self, path: str) -> FileStream:
        return self.disk("default").stream(path)

    def copy(self, src: str, destination: str) -> bool:
        return self.disk("default").copy(src, destination)

    def move(self, src: str, destination: str) -> bool:
        return self.disk("default").move(src, destination)

    def prepend(self, path: str, content: str) -> bool:
        return self.disk("default").prepend(path, content)

    def append(self, path: str, content: str) -> bool:
        return self.disk("default").append(path, content)

    def delete(self, path: str):
        return self.disk("default").delete(path)

    def make_directory(
        self, directory_path: str, mode="755", force=False, recursive=True
    ):
        return self.disk("default").make_directory(
            directory_path, mode, force, recursive
        )

    def delete_directory(self, directory_path: str, preserve: bool = False) -> bool:
        return self.disk("default").delete_directory(directory_path, preserve)

    def files(self, directory_path: str = "") -> "Collection[File]":
        return self.disk("default").files(directory_path)

    def all_files(self, directory_path: str = "") -> "Collection[File]":
        return self.disk("default").all_files(directory_path)

    def directories(self, directory_path: str = "") -> "Collection[str]":
        return self.disk("default").directories(directory_path)

    def get_url(self, path: str):
        return self.disk("default").get_url(path)

    # TODO:
    def response(self, file_path, name=None, headers={}, disposition="inline"):
        from src.masonite.facades import Response

        # return Response.

    # TODO:
    def download(self, file_path, name=None, headers={}):
        return self.disk().download(file_path, name, headers)
