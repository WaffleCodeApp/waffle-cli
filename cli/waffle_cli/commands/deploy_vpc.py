from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.vpc import generate_vpc_parameter_list, generate_vpc_stack_json
from .utils.deploy_new_stack import deploy_new_stack
from .command_type import Command


STACK_ID = "waffle-vpc"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployVpc(Command):
    name: str = "deploy_vpc"
    description: str = (
        "Generate a CFN template for a VPC and deploy it to the selected deployment. "
        "The default settings are based on the choice of deployment type, so that "
        "deploying different deployment types into the same AWS account and region "
        "don't lead to a conflict. You can override the default values if all the 5 "
        "CIDR related command line parameters settings are set."
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
            "--vpc_cidr",
            help="The CIDR of the vpc. (like for example: 10.51.0.0/16)",
            default="10.51.0.0/16",
        )
        parser.add_argument(
            "--primary_private_cidr",
            help="The CIDR of the primary private subnet. (like for example: 10.51.0.0/19)",
            default="10.51.0.0/19",
        )
        parser.add_argument(
            "--secondary_private_cidr",
            help="The CIDR of the secondary private subnet. (like for example: 10.51.32.0/19)",
            default="10.51.32.0/19",
        )
        parser.add_argument(
            "--primary_public_cidr",
            help="The CIDR of the primary public subnet. (like for example: 10.51.128.0/20)",
            default="10.51.128.0/20",
        )
        parser.add_argument(
            "--secondary_public_cidr",
            help="The CIDR of the secondary public subnet. (like for example: 10.51.144.0/20)",
            default="10.51.144.0/20",
        )
        parser.add_argument(
            "--custom_template_name",
            help="Optional. If there is a custom, already uploaded template for this purpose, specify its name.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        vpc_cidr: str | None = None,
        primary_private_cidr: str | None = None,
        secondary_private_cidr: str | None = None,
        primary_public_cidr: str | None = None,
        secondary_public_cidr: str | None = None,
        custom_template_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert vpc_cidr is not None
        assert primary_private_cidr is not None
        assert secondary_private_cidr is not None
        assert primary_public_cidr is not None
        assert secondary_public_cidr is not None

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=generate_vpc_stack_json,
            parameter_list=generate_vpc_parameter_list(
                deployment_id=deployment_id,
                vpc_cidr=vpc_cidr,
                primary_private_cidr=primary_private_cidr,
                secondary_private_cidr=secondary_private_cidr,
                primary_public_cidr=primary_public_cidr,
                secondary_public_cidr=secondary_public_cidr,
            ),
            stack_type=StackType.vpc,
            include_in_the_project=False,
        )
