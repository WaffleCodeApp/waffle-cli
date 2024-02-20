from argparse import ArgumentParser
import subprocess
from typing import Any

from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from .command_type import Command


class ConfigureAwsProfile(Command):
    name: str = "configure_aws_profile"
    description: str = (
        "Set AWS IAM credentials for local AWS CLI or AWS SDK use to access a deployment."
    )

    @staticmethod
    def arg_parser(
        parser: ArgumentParser, gateways: Gateways = gateway_implementations
    ) -> None:
        parser.add_argument(
            "deployment_id",
            help="An existing deployment ID that you add local credentials for",
            choices=gateways.deployment_settings.get_names(),
        )

    @staticmethod
    def execute(**kw: Any) -> None:
        deployment_id = kw.get("deployment_id")
        subprocess.run(f"aws configure --profile {deployment_id}".split())
