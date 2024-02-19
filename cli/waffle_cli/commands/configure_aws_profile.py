from argparse import ArgumentParser
import subprocess
from typing import Any
from .command_type import Command


class ConfigureAwsProfile(Command):
    name: str = "configure_aws_profile"
    description: str = (
        "Set AWS IAM credentials for AWS CLI or AWS SDK use to access a deployment"
    )

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "profile",
            help="Profile ID",
        )

    @staticmethod
    def execute(**kw: Any) -> None:
        profile = kw.get("profile")
        subprocess.run(f"aws configure --profile {profile}".split())
