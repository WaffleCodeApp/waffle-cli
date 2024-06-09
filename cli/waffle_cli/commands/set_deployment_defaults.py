from argparse import ArgumentParser
from typing import Any
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import NEUTRAL, RED
from .command_type import Command


class SetDeploymentDefaults(Command):
    name = "set_deployment_defaults"
    description = "Create settings for a new deployment"

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "deployment_id",
            help="A new deployment ID that will represent a complete environment in AWS. The id is recommended to be something like prod, dev, test, qa, etc.",
        )
        parser.add_argument(
            "--aws_region",
            help="AWS region to deploy to.",
            # aws ec2 describe-regions --profile dev
            choices=[
                "ap-south-1",
                "eu-north-1",
                "eu-west-3",
                "eu-west-2",
                "eu-west-1",
                "ap-northeast-3",
                "ap-northeast-2",
                "ap-northeast-1",
                "ca-central-1",
                "sa-east-1",
                "ap-southeast-1",
                "ap-southeast-2",
                "eu-central-1",
                "us-east-1",
                "us-east-2",
                "us-west-1",
                "us-west-2",
            ],
            required=True,
        )
        parser.add_argument(
            "--default_log_retention_days",
            help="Log retention to setting to be used by the stacks and components that are deployed with waffle. Default: 365",
            required=False,
            type=int,
            choices=[0, 7, 365],
        )
        parser.add_argument(
            "--default_alarms_enabled",
            help="Shall the stacks and components that are deployed with waffle trigger CloudWatch alarms? Default: True",
            required=False,
            choices=["True", "False"],
        )
        parser.add_argument(
            "--default_db_backup_retention",
            help="Backup retention to setting to be used by databases that are deployed with waffle. Default: 35",
            required=False,
            type=int,
            choices=[0, 7, 35],
        )
        parser.add_argument(
            "--default_require_manual_cicd_approval",
            help="Shall the CICD pipelines include an approval step before deployment? Default: True",
            required=False,
            choices=["True", "False"],
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        aws_region: str | None = None,
        default_log_retention_days: int | None = None,
        default_alarms_enabled: str | None = None,
        default_db_backup_retention: int | None = None,
        default_require_manual_cicd_approval: str | None = None,
        gateways: Gateways = gateway_implementations,
        **__: Any
    ) -> None:
        assert deployment_id is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is None:
            print(RED + "Settings not found for this deployment_id." + NEUTRAL)
            raise Exception("deployment_id not found")

        setting.aws_region = aws_region

        if default_log_retention_days is not None:
            setting.default_log_retention_days = default_log_retention_days

        if default_alarms_enabled is not None:
            setting.default_alarms_enabled = default_alarms_enabled == "True"

        if default_db_backup_retention is not None:
            setting.default_db_backup_retention = default_db_backup_retention

        if default_require_manual_cicd_approval is not None:
            setting.default_require_manual_cicd_approval = (
                default_require_manual_cicd_approval == "True"
            )

        gateways.deployment_settings.create_or_update(setting)
