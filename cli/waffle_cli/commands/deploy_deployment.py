from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.deployment import (
    generate_deployment_parameter_list,
    generate_deployment_stack_json,
)
from .command_type import Command
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-deployment"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployDeployment(Command):
    name: str = "deploy_deployment"
    description: str = (
        "Generate a CFN template for deployment-wide shared resources. "
        "This stack provides an empty secret that can be easily accesed from any backend componetns "
        "that are deployed with Waffle."
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
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name=TEMPLATE_NAME,
            generate_stack_json=generate_deployment_stack_json,
            parameter_list=generate_deployment_parameter_list(
                deployment_id=deployment_id,
            ),
            stack_type=StackType.deployment,
            include_in_the_project=False,
        )
