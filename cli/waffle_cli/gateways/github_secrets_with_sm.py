from application_logic.entities.github_secret import GithubSecret
from ..application_logic.gateway_interfaces.github_secrets import GitHubSecrets
from typing import Any
from boto3 import Session  # pyright: ignore[reportMissingTypeStubs]


class GitHubSecretsWithSM(GitHubSecrets):
    def _get_client(self, deployment_id: str, aws_region: str) -> Any:
        return Session(profile_name=deployment_id).client(  # type: ignore
            "secretsmanager",
            region_name=aws_region,
        )

    def store_access_token(
        self,
        deployment_id: str,
        aws_region: str,
        secret_arn: str,
        access_token: str,
    ) -> None:
        github_secret = GithubSecret(github_access_token=access_token)
        client = self._get_client(deployment_id, aws_region)
        client.put_secret_value(
            Name=secret_arn,
            SecretString=github_secret.model_dump_json(),
        )

    def get_secret_arn_from_physical_resource_id(
        self,
        deployment_id: str,
        aws_region: str,
        physical_resource_id: str,
    ) -> str:
        client = self._get_client(deployment_id, aws_region)
        secret_details = client.describe_secret(SecretId=physical_resource_id)
        secret_arn = secret_details["ARN"]
        return secret_arn
