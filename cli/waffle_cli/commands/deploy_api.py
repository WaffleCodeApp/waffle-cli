from argparse import ArgumentParser
from typing import Any


from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.entities.stack_type import StackType
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
            "--custom_certificate_arn",
            help="Optional. The arn of the generic certificate that can be used for the full domain name and its subdomains. If omitted then the one generated by waffle is being used.",
        )
        parser.add_argument(
            "--custom_template_name",
            help="Optional. If there is a custom, already uploaded template for this purpose, specify its name.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        api_subdomain: str | None = None,
        custom_certificate_arn: str | None = None,
        custom_template_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert api_subdomain is not None

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

        deployment_state: DeploymentState = gateways.deployment_states.get(
            deployment_id
        ) or DeploymentState(deployment_id=deployment_id)

        if (
            deployment_state.generic_certificate_arn is None
            and custom_certificate_arn is None
        ):
            print(
                RED
                + "An SSL certificate has to be either generated by waffle first, or the custom_certificate_arn has to be specified."
                + NEUTRAL
            )
            raise Exception("No cert arn found")

        cert_arn = custom_certificate_arn or deployment_state.generic_certificate_arn
        assert cert_arn is not None
        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=STACK_ID,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=generate_api_stack_json,
            parameter_list=generate_api_parameter_list(
                deployment_id=deployment_setting.deployment_id,
                full_domain_name=deployment_setting.full_domain_name,
                api_subdomain=api_subdomain,
                certificate_arn=cert_arn,
            ),
            stack_type=StackType.api,
            include_in_the_project=False,
        )
