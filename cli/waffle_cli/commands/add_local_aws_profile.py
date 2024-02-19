from argparse import ArgumentParser
import subprocess
from typing import Any

from .command_type import Command

NAME = "configure_aws_profile"
DESCRIPTION = (
    "Set AWS IAM credentials for AWS CLI or AWS SDK use to access a deployment"
)


class ConfigureAwsProfile(Command):
    @staticmethod
    def get_name() -> str:
        return NAME

    @staticmethod
    def get_descrtiption() -> str:
        return DESCRIPTION

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "profile",
            help="Profile ID",
        )

    @staticmethod
    def execute(**kw: dict[str, Any]) -> None:
        profile = kw.get("profile")
        subprocess.run(f"aws configure --profile {profile}".split())
