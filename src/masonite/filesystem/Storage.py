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

    def get_path(self, path):
        # TODO:???
        return

    def get_name(self, path, alias):
        # TODO ?????
        return

    def put(self, file_path, content):
        return relative_path

    def put_file(self, file_path, content, name=None):
        return relative_path

    def get(self, file_path: str):
        return self.disk().get(file_path)

    def exists(self, file_path):
        return os.path.exists(self.get_path(file_path))

    def missing(self, file_path):
        return not self.exists(file_path)

    def download(self, file_path, name=None, headers={}):
        return self.disk().download(file_path, name, headers)

    def stream(self, file_path):
        return FileStream(content)

    def copy(self, from_file_path, to_file_path):
        return

    def move(self, from_file_path, to_file_path):
        return

    def prepend(self, file_path, content):
        return

    def append(self, file_path, content):
        return

    def delete(self, file_path):
        return

    def make_directory(self, directory):
        pass

    def store(self, file, name=None):
        return relative_path

    def make_file_path_if_not_exists(self, file_path):
        return

    def get_files(self, directory=""):
        return files

    def get_url(self, path: str):
        return self.disk().get_url()
