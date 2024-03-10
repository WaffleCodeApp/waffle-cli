from argparse import ArgumentParser
from typing import Any

from application_logic.entities.deployment_setting import DeploymentSetting
from application_logic.entities.stack_settings.api_stack_setting import ApiStackSetting
from application_logic.entities.stack_type import StackType
from application_logic.gateway_interfaces import Gateways
from gateways import gateway_implementations
from templates.api import generate_api_parameter_list, generate_api_stack_json
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
            "--full_domain_name",
            help="Required for first setup. The topmost DNS name under which this deployment's subdomains are created. Like for example: dev.example.com",
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
        full_domain_name: str | None = None,
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
            raise Exception("setting not found for deployment_id")

        if not setting.template_bucket_name:
            raise Exception("Template bucket name is None")

        if not setting.aws_region:
            raise Exception("AWS region is None")

        if not setting.deployment_type:
            raise Exception("Deployment type is None")

        if setting.api_stack_setting is None and api_subdomain is None:
            raise Exception("api_subdomain has to be specified for the first run")

        if certificate_arn is None and setting.generic_certificate_arn is None:
            raise Exception(
                "No generic certificate is known, required to specify with the generic_certificate_arn option"
            )

        if full_domain_name is None and setting.full_domain_name is None:
            raise Exception(
                "full_domain_name is not set, required to specify with the full_domain_name option"
            )

        gateways.deployment_template_bucket.create_bucket_if_not_exist(
            deployment_id, setting.template_bucket_name, setting.aws_region
        )

        api_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=setting.template_bucket_name,
            aws_region=setting.aws_region,
            key="api-template.json",
            content=generate_api_stack_json(),
        )

        if setting.api_stack_setting is None:
            setting.api_stack_setting = ApiStackSetting(
                subdomain=api_subdomain,  # type: ignore
            )

        gateways.deployment_settings.create_or_update(setting)

        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=api_template_url,
            setting=setting,
            parameters=generate_api_parameter_list(
                deployment_id=setting.deployment_id,
                full_domain_name=full_domain_name or setting.full_domain_name,  # type: ignore
                api_subdomain=setting.api_stack_setting.subdomain,  # type: ignore
                certificate_arn=certificate_arn or setting.generic_certificate_arn,  # type: ignore
            ),
            stack_type=StackType.api,
        )

        setting.api_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)
