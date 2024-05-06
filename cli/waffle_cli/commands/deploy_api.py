from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.cfn_stack_state import CfnStackState
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.entities.stack_settings.api_stack_setting import ApiStackSetting
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.api import generate_api_parameter_list, generate_api_stack_json
from ..utils.std_colors import BLUE, BOLD, GREEN, NEUTRAL, RED
from .command_type import Command


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

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is None:
            print(RED + f'Settings for {deployment_id} not found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("Setting not found for deployment_id")

        if setting.aws_region is None:
            print(RED + 'AWS region setting not found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("AWS region is None")

        if setting.full_domain_name is None:
            print(RED + "Full domain name setting not found. Please make sure to run configure_deployment_domain first." + NEUTRAL)
            raise Exception("full_domain_name is None")

        state: DeploymentState | None = gateways.deployment_states.get(deployment_id)
        if state is None:
            print(
                RED
                + f"State for {deployment_id} not found. This seems to be a bug."
                + NEUTRAL
            )
            raise Exception("State not found for deployment_id")

        if state.template_bucket_name is None:
            print(RED + "Template bucket name setting not found. Please make sure to run configure_deployment_domain first." + NEUTRAL)
            raise Exception("template_bucket_name is None")

        i_api_subdomain = api_subdomain
        if setting.api_stack_setting is None and api_subdomain is None:
            print(BLUE + BOLD)
            i_api_subdomain = input("Please specify the backend api's subdomain name. Like for example: 'api' from 'api.dev.example.com'. Recommended for most cases: 'api'. ")
            print(NEUTRAL)

        i_certificate_arn = certificate_arn
        if certificate_arn is None and state.generic_certificate_arn is None:
            print(RED + "Generic certificate setting not found. Please make sure to run create_deployment_certificate first. Alternatively you can specify a custom certificate ARN for the API specifically:" + BLUE + BOLD)
            i_certificate_arn = input('Custom certificate ARN for the API: ')
            print(NEUTRAL)
    
        if setting.api_stack_setting is None:
            assert i_api_subdomain is not None
            setting.api_stack_setting = ApiStackSetting(
                subdomain=i_api_subdomain,
                custom_certificate_arn=i_certificate_arn
            )
        else:
            if i_api_subdomain is not None:
                setting.api_stack_setting.subdomain = i_api_subdomain
            if i_certificate_arn is not None:
                setting.api_stack_setting.custom_certificate_arn = i_certificate_arn

        gateways.deployment_settings.create_or_update(setting)

        certificate_arn = setting.api_stack_setting.custom_certificate_arn or state.generic_certificate_arn
        assert certificate_arn is not None

        gateways.deployment_template_bucket.create_bucket_if_not_exist(
            deployment_id, state.template_bucket_name, setting.aws_region
        )

        api_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=state.template_bucket_name,
            aws_region=setting.aws_region,
            key="api-template.json",
            content=generate_api_stack_json(),
        )

        gateways.deployment_settings.create_or_update(setting)


        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=api_template_url,
            setting=setting,
            parameters=generate_api_parameter_list(
                deployment_id=setting.deployment_id,
                full_domain_name=setting.full_domain_name,
                api_subdomain=setting.api_stack_setting.subdomain,
                certificate_arn=certificate_arn
            ),
            stack_type=StackType.api,
        )

        state.api_stack_state = CfnStackState(cfn_stack_id=cfn_stack_id)
        gateways.deployment_states.create_or_update(state)

        print(GREEN + 'Done. The deployment typically takes a few minutes.\n' + NEUTRAL)
