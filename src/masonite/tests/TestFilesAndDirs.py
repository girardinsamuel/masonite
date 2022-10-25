import os
import tempfile


class TestFilesAndDirs:

    work_directory = "storage/framework/filesystem/testing/"

    def tearDown(self):
        """Empty work directory between each test."""
        super().tearDown()
        self.create_tmp_work_directory()

    def create_tmp_work_directory(self):
        # create temporary directory to work with. It will be automatically deleted at test end
        self.tmp_dir = tempfile.TemporaryDirectory(dir=self.work_directory)
        self.tmp_root_dir = self.tmp_dir.name

    def startTestRun(self):
        self.create_tmp_work_directory()
        return self

    def get_path(self, path: str = ""):
        return os.path.join(self.tmp_root_dir, path)

    def stopTestRun(self):
        return self
