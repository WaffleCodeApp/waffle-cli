from argparse import ArgumentParser
from typing import Any
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_type import DeploymentType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import GREEN, NEUTRAL, RED
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
        parser.add_argument(
            "--aws_region",
            help="AWS region to deploy to. Default: us-east-1",
            choices=['ap-south-1', 'eu-north-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-3', 'ap-northeast-2', 'ap-northeast-1', 'ca-central-1', 'sa-east-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        deployment_type: DeploymentType | None = None,
        aws_region: str | None = None,
        gateways: Gateways = gateway_implementations,
        **__: Any
    ) -> None:
        assert deployment_id is not None
        assert deployment_type is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is not None:
            print(RED + 'Settings found for this deployment_id. This command only has to be run once per deployment.' + NEUTRAL)
            raise Exception("deployment_id already exists")

        gateways.deployment_settings.create_or_update(
            DeploymentSetting(
                deployment_id=deployment_id, deployment_type=deployment_type
            )
        )
        if aws_region is not None:
            setting: DeploymentSetting | None = gateways.deployment_settings.get(
                deployment_id
            )
            assert setting is not None
            setting.aws_region = aws_region
            gateways.deployment_settings.create_or_update(setting)

        print(GREEN + 'Done.\n' + NEUTRAL)

