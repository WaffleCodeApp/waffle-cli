from argparse import ArgumentParser
from typing import Any
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import GREEN, NEUTRAL, RED
from .command_type import Command


class CreateDeploymentCertificate(Command):
    name = "create_deployment_certificate"
    description = "Create an SSL certificate with AWS Certificate Manager for domain name of the deployment. This will be used by AWS services for HTTPS."

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
        **_: Any
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

        if setting.generic_certificate_arn:
            print(RED + 'The generic certificate ARN found in the settings. This indicates that this command has already been run for this deployment.' + NEUTRAL)
            raise Exception("Certificate already created")

        generic_certificate_arn = gateways.certs.request_cert_and_get_arn(
            deployment_id=deployment_id,
            full_domain_name=setting.full_domain_name,
            aws_region=setting.aws_region,
        )

        setting.generic_certificate_arn = generic_certificate_arn

        gateways.deployment_settings.create_or_update(setting)

        print(GREEN + 'Done. The certification validation may take a few minutes.\n' + NEUTRAL)
