from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import NEUTRAL, RED
from .command_type import Command


class CreateDeploymentSettings(Command):
    name = "create_deployment_settings"
    description = "Create an empty settings configuration for a new deployment"

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "deployment_id",
            help="A new deployment ID that will represent a complete environment in AWS. The id is recommended to be something like prod, dev, test, qa, etc.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        gateways: Gateways = gateway_implementations,
        **__: Any
    ) -> None:
        assert deployment_id is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is not None:
            print(
                RED
                + "Settings found for this deployment_id. This command only has to be run once per deployment."
                + NEUTRAL
            )
            raise Exception("deployment_id already exists")

        gateways.deployment_settings.create_or_update(
            DeploymentSetting(deployment_id=deployment_id)
        )
        deployment_state: DeploymentState = gateways.deployment_states.get(
            deployment_id
        ) or DeploymentState(deployment_id=deployment_id)
        gateways.deployment_states.create_or_update(deployment_state)
