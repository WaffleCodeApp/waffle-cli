from typing import Protocol


class GitHubSecrets(Protocol):
    def store_api_key(self, deployment_id: str, api_key: str) -> None: ...
