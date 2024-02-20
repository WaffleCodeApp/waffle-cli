from typing import Protocol
from ..entities.deployment_setting import DeploymentSetting


class DeploymentSettings(Protocol):
    def create_or_update(self, deployment_setting: DeploymentSetting) -> None: ...

    def get(self, deployment_id: str) -> DeploymentSetting | None: ...

    def get_names(self) -> list[str]: ...
