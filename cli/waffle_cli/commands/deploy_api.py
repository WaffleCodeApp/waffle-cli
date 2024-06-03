from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.api import generate_api_parameter_list, generate_api_stack_json
from ..utils.std_colors import NEUTRAL, RED
from .command_type import Command
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-api"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployApi(Command):
    name: str = "deploy_api"
    description: str = (
        "Generate a CFN template for an API Gateway and deploy it to the selected deployment. "
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
            "--api_subdomain",
            help="Required for first setup. The backend api's DNS identifier. Like for example: 'api' from 'api.dev.example.com'. Recommended for most cases: 'api'.",
        )
        parser.add_argument(
            "--certificate_arn",
            help="Optional. The arn of the generic certificate that can be used for the full domain name and its subdomains. If omitted then the one generated by waffle is being used.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        api_subdomain: str | None = None,
        certificate_arn: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert api_subdomain is not None
        assert certificate_arn is not None

        deployment_setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if deployment_setting is None:
            print(
                RED
                + f"Settings for {deployment_id} not found. Please make sure to run create_deployment_settings first."
                + NEUTRAL
            )
            raise Exception("Setting not found for deployment_id")

        if deployment_setting.full_domain_name is None:
            print(
                RED
                + "Full domain name setting not found. Please make sure to run configure_deployment_domain first."
                + NEUTRAL
            )
            raise Exception("full_domain_name is None")

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name_default=TEMPLATE_NAME,
            generate_stack_json=generate_api_stack_json,
            parameter_list=generate_api_parameter_list(
                deployment_id=deployment_setting.deployment_id,
                full_domain_name=deployment_setting.full_domain_name,
                api_subdomain=api_subdomain,
                certificate_arn=certificate_arn,
            ),
        )
