import os
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..foundation import Application
    from boto3 import Session as S3Session, Bucket as S3Bucket
from ..FileStream import FileStream
from ..File import File
from ...utils.filesystem import FileSystem


class AmazonS3Driver:
    def __init__(self, application: "Application"):
        self.application = application
        self.options = {}
        self.connection = None

    def set_options(self, options: dict):
        self.options = options
        return self

    def get_connection(self) -> S3Session:
        """Get a S3 session instance object."""
        try:
            import boto3
        except ImportError:
            raise ModuleNotFoundError(
                "Could not find the 'boto3' library. Run 'pip install boto3' to fix this."
            )

        if not self.connection:
            self.connection = boto3.Session(
                aws_access_key_id=self.options.get("client"),
                aws_secret_access_key=self.options.get("secret"),
                region_name=self.options.get("region"),
            )

        return self.connection

    def get_bucket_name(self) -> str:
        """Get S3 bucket name for the configured disk."""
        return self.options.get("bucket")

    def get_bucket(self) -> S3Bucket:
        return self.get_connection().resource("s3").Bucket(self.get_bucket_name())

    def get_name(self, path: str, alias: str = None):
        extension = FileSystem.extension(path)
        filename = FileSystem.filename(path)
        if alias:
            filename = alias
        return f"{filename}{extension}"

    def put(self, path: str, content: str | bytes | bytearray) -> bool:
        self.get_bucket().put_object(Key=path, Body=content)
        return True

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
            return (
                self.get_bucket().Object(path).get().get("Body").read().decode("utf-8")
            )
        except self.missing_file_exceptions():
            return None

    def missing_file_exceptions(self):
        import boto3

        return (boto3.exceptions.botocore.errorfactory.ClientError,)

    def exists(self, path: str) -> bool:
        try:
            self.get_bucket().Object(path).get().get("Body").read()
            return True
        except self.missing_file_exceptions():
            return False

    def missing(self, path: str) -> bool:
        return not self.exists(path)

    def stream(self, path: str) -> FileStream:
        return FileStream(
            self.get_bucket().Object(file_path).get().get("Body").read(),
            path,
        )

    def copy(self, src: str, destination: str) -> bool:
        copy_source = {"Bucket": self.get_bucket_name(), "Key": src}
        self.get_connection().resource("s3").meta.client.copy(
            copy_source, self.get_bucket_name(), destination
        )
        return True

    def move(self, src: str, destination: str) -> bool:
        self.copy(src, destination)
        self.delete(src)
        return True

    def prepend(self, path: str, content: str) -> bool:
        value = self.get(path) or ""
        content = content + value
        return self.put(path, content)

    def append(self, path: str, content: str) -> bool:
        value = self.get(path) or ""
        value += content
        return self.put(path, content)

    def delete(self, path: str) -> bool:
        return (
            self.get_connection()
            .resource("s3")
            .Object(self.get_bucket_name(), path)
            .delete()
        )

    def files(self, directory_path: str = "") -> "Collection[File]":
        bucket = self.get_bucket()

        if directory_path:
            objects = bucket.objects.all().filter(Prefix=directory_path)
        else:
            objects = bucket.objects.all()

        files = Collection()
        for bucket_obj in objects.all():
            if "/" not in bucket_obj.key:
                # TODO: check where is the path here
                files.push(File(bucket_obj.key))
        return files
