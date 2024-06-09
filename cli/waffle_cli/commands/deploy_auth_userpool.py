from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.authentication import (
    generate_auth_stack_json,
    generate_auth_parameter_list,
)
from .utils.deploy_new_stack import deploy_new_stack
from .command_type import Command


STACK_ID = "waffle-auth-userpool"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployAuthUserPool(Command):
    name: str = "deploy_auth_userpool"
    description: str = (
        "Generate a CFN template for authentication and deploy it to the selected deployment. "
        "This stack is required if you want to enable IAM authentication on the API Gateway, "
        "and use it from a frontend application. This template deploys a Cognito "
        "User Pool, the user authentication service provided by AWS. IF you with to use a different "
        "solution, like OIDC authentication, you need to bring your own template for now. "
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
        parser.add_argument(
            "--custom_template_name",
            help="Optional. If there is a custom, already uploaded template for this purpose, specify its name.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        custom_template_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=generate_auth_stack_json,
            parameter_list=generate_auth_parameter_list(
                deployment_id=deployment_id,
                create_userpool="True",
            ),
            stack_type=StackType.auth,
            include_in_the_project=False,
        )
