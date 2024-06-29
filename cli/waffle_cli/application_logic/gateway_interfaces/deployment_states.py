from typing import Protocol
from ..entities.deployment_state import DeploymentState


class DeploymentStates(Protocol):
    def create_or_update(self, deployment_state: DeploymentState) -> None: ...

    def get(self, deployment_id: str) -> DeploymentState | None: ...
