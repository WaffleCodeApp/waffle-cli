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

    def wait_for_stacks_to_create_or_update(
        self,
        deployment_id: str,
        aws_region: str,
        cfn_stack_ids: list[str] | None = None,
    ) -> bool: ...

    def get_physical_resource_id_from_stack(
        self,
        deployment_id: str,
        aws_region: str,
        cfn_stack_id: str,
        logical_resource_id: str,
    ) -> str: ...
