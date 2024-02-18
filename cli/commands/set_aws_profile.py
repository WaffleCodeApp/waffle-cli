from argparse import ArgumentParser
import subprocess


def set_arg_parser(parser: ArgumentParser):
    parser.add_argument(
        "profile",
        help="Profile ID",
    )

def set_aws_profile(profile_id: str):
    subprocess.run(f'aws configure --profile {profile_id}'.split())
