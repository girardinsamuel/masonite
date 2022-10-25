from . import Storage
from typing import TYPE_CHECKING
import tempfile
import shutil
from .drivers import LocalDriver
from ..utils.location import base_path

if TYPE_CHECKING:
    from ..foundation import Application


class MockStorage(Storage):
    def __init__(self, application: "Application", store_config: dict = None):
        super().__init__(application, store_config)
        self.temp_dirs = {}

    def flush_all(self):
        """Reset mock implementation."""
        for tmp_dir_name in self.temp_dirs.keys():
            self.flush(tmp_dir_name)

    def get_storage_root(self, name):
        return base_path(self.temp_dirs.get(name).name)

    def flush(self, name="local"):
        root_path = self.get_storage_root(name)
        shutil.rmtree(root_path, ignore_errors=True)

    def create_temp_dir_if_not_exists(self, name):
        if name not in self.temp_dirs:
            temp_dir = tempfile.TemporaryDirectory(
                dir="storage/framework/filesystem/testing", prefix=name + "_"
            )
            self.temp_dirs.update({name: temp_dir})
            return base_path(temp_dir.name)
        else:
            return base_path(self.temp_dirs.get(name).name)

    def disk(self, name: str = "local"):
        """Provide a disk using local driver configured with a tmp directory automatically
        deleted when tests are done."""
        # create temp dir if needed
        temp_dir = self.create_temp_dir_if_not_exists(name)
        driver = LocalDriver(self.application)
        return driver.set_options(
            {
                "path": temp_dir,
            }
        )

    def assertExists(self, name: str, disk: str = "local") -> None:
        assert self.disk(disk).exists(name)

    def assertMissing(self, name: str, disk: str = "local") -> None:
        assert self.disk(disk).missing(name)
