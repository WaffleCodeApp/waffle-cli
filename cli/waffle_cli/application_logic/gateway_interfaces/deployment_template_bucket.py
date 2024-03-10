from typing import Protocol


class DeploymentTemplateBucket(Protocol):
    def create_bucket_if_not_exist(
        self, deployment_id: str, bucket_name: str, aws_region: str
    ) -> None: ...

    def upload_file(
        self, deployment_id: str, bucket_name: str, aws_region: str, file_path: str
    ) -> None: ...

    def upload_obj(
        self,
        deployment_id: str,
        bucket_name: str,
        aws_region: str,
        key: str,
        content: str,
    ) -> str: ...

    def get_url_base(self, bucket_name: str) -> str: ...
