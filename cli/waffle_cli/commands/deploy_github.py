from argparse import ArgumentParser
from typing import Any

from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.github import (
    generate_github_parameter_list,
    generate_github_stack_json,
)
from .command_type import Command
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-github"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployGithub(Command):
    name: str = "deploy_github"
    description: str = (
        "Generate a CFN template for accessing repositories from GitHub for CICD. "
        "This stack installs a secret that holds the github credentials. "
        "This secret is used by CodePipeline components of other stacks."
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
    def execute(
        deployment_id: str | None = None,
        wait_to_finish: bool = False,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name_default=TEMPLATE_NAME,
            generate_stack_json=generate_github_stack_json,
            parameter_list=generate_github_parameter_list(
                deployment_id=deployment_id,
            ),
        )

        if wait_to_finish:
            deployment_setting = gateways.deployment_settings.get(deployment_id)
            assert deployment_setting is not None
            assert deployment_setting.aws_region is not None

            gateways.stacks.wait_for_stacks_to_create_or_update(
                deployment_id, deployment_setting.aws_region, [STACK_ID]
            )
