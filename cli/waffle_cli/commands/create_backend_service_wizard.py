from argparse import ArgumentParser
import re
from typing import Any

from commands.deploy_ecs import DeployEcs

from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import BOLD, NEUTRAL, RED, YELLOW
from .command_type import Command


class CreateBackendServiceWizard(Command):
    name = "create_backend_service_wizard"
    description = "Step-by-step specify a backend serivce and deploy it into an existing Waffle deployment."

    @staticmethod
    def arg_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def execute(gateways: Gateways = gateway_implementations, **__: Any) -> None:
        print(
            NEUTRAL
            + "Waffle is a toolkit to help deploy complete web-applications to secure "
            + "environments in AWS.\n\n"
            + "This tool helps you add a backend service to one of your existing "
            + "deployments as a set of ECS Fargate instances step-by-step interactively.\n\n"
            + YELLOW
            + "If you want to use custom templates or existing resources, then "
            + "you need to do a custom installation, prease refer to the docs.\n\n"
            + NEUTRAL
        )

        deployment_ids = gateways.deployment_settings.get_names()
        if len(deployment_ids) == 0:
            print(
                RED
                + "Couldn't find any deployments. Please start with creating at "
                + "least one deployment.\n\n"
                + NEUTRAL
                + "You can create a new deployment with the create_deployment_wizard "
                + "command.\n\n"
            )
            return

        print(
            BOLD
            + "To which deployment do you want to install a frontend?\n\n"
            + NEUTRAL
            + "The following deployments were found:\n"
            + "\n".join([f"\t- {d}" for d in deployment_ids])
            + "\n\n"
        )
        deployment_id: str = ""
        while True:
            deployment_id = input(
                "Please choose a deployment from the list above or type done: "
            )
            if deployment_id in deployment_ids:
                break
            else:
                print(
                    RED
                    + "Deployment choice not reconized, please use one of the list above."
                    + NEUTRAL
                )

        print("\n\n" + NEUTRAL)
        pipeline_id: str = ""
        while True:
            pipeline_id = input("Choose an id for this service: ")
            if pipeline_id != "" and re.match(r"^[a-z,0-9]+$", pipeline_id):
                break
            print(RED + "Only letters and numbers are supported." + NEUTRAL)
        print("\n\n")
        github_url: str = ""
        github_owner: str = ""
        github_repo_name: str = ""
        github_branch: str = ""
        buildspec_path: str = ""
        while True:
            pattern = r"https?://github\.com/([^/]+)/([^/]+)"
            github_url = input("The URL of the repository on github to deploy: ")
            match = re.match(pattern, github_url)
            if match:
                github_owner = match.group(1)
                github_repo_name = match.group(2)
                break
            print(RED + "Only github repositry URLs are accepted." + NEUTRAL)
        while True:
            github_branch = input("The branch to deploy: ")
            if github_branch != "":
                break
        while True:
            buildspec_path = input(
                "The path to the buildspec.yml file including the filename: "
            )
            if buildspec_path != "":
                break
        DeployEcs.execute(
            deployment_id=deployment_id,
            pipeline_id=pipeline_id,
            github_owner=github_owner,
            github_repo_name=github_repo_name,
            github_branch=github_branch,
            buildspec_path=buildspec_path,
        )
