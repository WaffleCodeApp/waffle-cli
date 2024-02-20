from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_type import DeploymentType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from .command_type import Command


class SetDeploymentType(Command):
    name = "set_deployment_type"
    description = "Set default values by selecting a deployment type"

    @staticmethod
    def arg_parser(
        parser: ArgumentParser, gateways: Gateways = gateway_implementations
    ) -> None:
        parser.add_argument(
            "deployment_id",
            help="An existing deployment ID that you add local credentials for",
            choices=gateways.deployment_settings.get_names(),
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
        **_: Any
    ) -> None:
        assert deployment_id is not None
        assert deployment_type is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is None:
            raise Exception("setting not found for deployment_id")

        setting.deployment_type = deployment_type

        gateways.deployment_settings.create_or_update(setting)
