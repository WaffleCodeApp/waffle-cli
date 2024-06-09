from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.cfn_stack_state import CfnStackState
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.entities.stack_type import StackType
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
        parser.add_argument("access_token", help="GitHub access token", default="")

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        access_token: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert access_token is not None

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name=TEMPLATE_NAME,
            generate_stack_json=generate_github_stack_json,
            parameter_list=generate_github_parameter_list(
                deployment_id=deployment_id,
            ),
            stack_type=StackType.github,
            include_in_the_project=False,
        )

        deployment_setting = gateways.deployment_settings.get(deployment_id)
        assert deployment_setting is not None
        assert deployment_setting.aws_region is not None

        gateways.stacks.wait_for_stacks_to_create_or_update(
            deployment_id, deployment_setting.aws_region, [STACK_ID]
        )

        deployment_state: DeploymentState = gateways.deployment_states.get(
            deployment_id
        ) or DeploymentState(deployment_id=deployment_id)

        deployment_stack: CfnStackState | None = next(
            (stack for stack in deployment_state.stacks if stack.stack_id == STACK_ID),
            None,
        )

        assert deployment_stack is not None

        secret_physical_resource_id = (
            gateways.stacks.get_physical_resource_id_from_stack(
                deployment_id=deployment_id,
                aws_region=deployment_setting.aws_region,
                cfn_stack_id=deployment_stack.cfn_stack_id,
                logical_resource_id="GithubSecret",
            )
        )
        secret_arn = gateways.github_secrets.get_secret_arn_from_physical_resource_id(
            deployment_id=deployment_id,
            aws_region=deployment_setting.aws_region,
            physical_resource_id=secret_physical_resource_id,
        )
        gateways.github_secrets.store_access_token(
            deployment_id=deployment_id,
            aws_region=deployment_setting.aws_region,
            secret_arn=secret_arn,
            access_token=access_token,
        )
