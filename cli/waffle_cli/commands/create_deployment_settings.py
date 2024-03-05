from argparse import ArgumentParser
from typing import Any
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_type import DeploymentType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from .command_type import Command


class CreateDeploymentSettings(Command):
    name = "create_deployment_settings"
    description = "Create settings for a new deployment"

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "deployment_id",
            help="A new deployment ID that will represent a complete environment in AWS. The id is recommended to be something like prod, dev, test, qa, etc.",
        )
        parser.add_argument(
            "deployment_type",
            help="Type of the deployment: DEV for development, PROD for production. This value is used by stacks to set default logging, monitoring behavior and other default values.",
            choices=[t.name for t in DeploymentType],
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        deployment_type: DeploymentType | None = None,
        gateways: Gateways = gateway_implementations,
        **__: Any
    ) -> None:
        assert deployment_id is not None
        assert deployment_type is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is not None:
            raise Exception("deployment_id already exists")
        gateways.deployment_settings.create_or_update(
            DeploymentSetting(
                deployment_id=deployment_id, deployment_type=deployment_type
            )
        )
