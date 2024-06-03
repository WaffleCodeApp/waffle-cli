from typing import Protocol
from ..entities.cfn_stack_state import CfnStackState
from ..entities.deployment_setting import DeploymentSetting


class Stacks(Protocol):
    def create_or_update_stack(
        self,
        deployment_setting: DeploymentSetting,
        template_url: str,
        stack_id: str,
        stack_state: CfnStackState | None,
        parameters: list[dict[str, str]],
    ) -> str: ...
