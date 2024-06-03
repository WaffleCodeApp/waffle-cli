from ..application_logic.gateway_interfaces.github_secrets import GitHubSecrets
from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]
from boto3.session import Config  # pyright: ignore[reportMissingTypeStubs]


class GitHubSecretsWithSM(GitHubSecrets):
    def _get_client(self, deployment_id: str, aws_region: str) -> Any:
        return Session(profile_name=deployment_id).client(  # type: ignore
            "ssm", region_name=aws_region, config=Config(signature_version="s3v4")  # type: ignore
        )

    def store_api_key(
        self,
        deployment_id: str,
        api_key: str,
    ) -> None:
        pass
