from argparse import ArgumentParser
import subprocess
from typing import Any


def add_aws_profile_arg_parser(parser: ArgumentParser):
    parser.add_argument(
        "profile",
        help="Profile ID",
    )


def add_aws_profile(profile: str, **_: dict[str, Any]):
    subprocess.run(f"aws configure --profile {profile}".split())
