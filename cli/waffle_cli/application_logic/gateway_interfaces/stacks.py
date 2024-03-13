from typing import Protocol

from ..entities.deployment_setting import DeploymentSetting
from ..entities.stack_type import StackType


class Stacks(Protocol):
    def create_or_update_stack(
        self,
        template_url: str,
        setting: DeploymentSetting,
        parameters: list[dict[str, str]],
        stack_type: StackType,
        pipeline_name: str | None = None,
    ) -> str: ...
