from argparse import ArgumentParser
from typing import Any
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
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
            raise Exception("setting not found for deployment_id")

        if setting.generic_certificate_arn:
            raise Exception("Certificate already created")

        if not setting.full_domain_name:
            raise Exception("Full domain name is None")

        if not setting.aws_region:
            raise Exception("AWS region is None")

        generic_certificate_arn = gateways.certs.request_cert_and_get_arn(
            deployment_id=deployment_id,
            full_domain_name=setting.full_domain_name,
            aws_region=setting.aws_region,
        )

        setting.generic_certificate_arn = generic_certificate_arn

        gateways.deployment_settings.create_or_update(setting)
