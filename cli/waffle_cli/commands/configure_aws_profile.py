from argparse import ArgumentParser
import subprocess
from typing import Any
from .command_type import Command


class ConfigureAwsProfile(Command):
    name: str = "configure_aws_profile"
    description: str = (
        "Set AWS IAM credentials for local AWS CLI or AWS SDK use to access a deployment."
    )

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "deployment_id",
            help="Deployment ID, like for example prod, dev, test, qa, etc.",
        )

    @staticmethod
    def execute(**kw: Any) -> None:
        deployment_id = kw.get("deployment_id")
        subprocess.run(f"aws configure --profile {deployment_id}".split())
