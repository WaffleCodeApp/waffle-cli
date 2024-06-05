from typing import Protocol


class GitHubSecrets(Protocol):
    def store_access_token(
        self,
        deployment_id: str,
        aws_region: str,
        secret_arn: str,
        access_token: str,
    ) -> None: ...

    def get_secret_arn_from_physical_resource_id(
        self,
        deployment_id: str,
        aws_region: str,
        physical_resource_id: str,
    ) -> str: ...
