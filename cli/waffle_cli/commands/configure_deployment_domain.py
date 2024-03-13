from argparse import ArgumentParser
from typing import Any
import uuid
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import BLUE, BOLD, GREEN, NEUTRAL, RED
from .command_type import Command


class ConfigureDeploymentDomain(Command):
    name = "configure_deployment_domain"
    description = "Create an AWS Route 53 hosted zome for the deployment DNS settings"

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
            "full_domain_name",
            help="The full domain name where this deployment will be hosted (like dev.example.com). Heads-up: additional subdomains will be created under this domain name (like api.dev.example.com).",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        full_domain_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any
    ) -> None:
        assert deployment_id is not None
        assert full_domain_name is not None

        setting: DeploymentSetting | None = gateways.deployment_settings.get(
            deployment_id
        )
        if setting is None:
            print(RED + f'Settings for {deployment_id} not found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("Setting not found for deployment_id")

        if setting.deployment_type is None:
            print(RED + 'Deployment type setting found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("Deployment type is None")

        if setting.ns_list:
            print(RED + 'NS related settings found, which indicates that configure_deployment_domain has already been run.' + NEUTRAL)
            raise Exception("Domain is already set up")

        ns_list = gateways.hosted_zones.create_hosted_zone_and_get_ns_list(
            deployment_id=deployment_id, full_domain_name=full_domain_name
        )

        setting.full_domain_name = full_domain_name
        setting.ns_list = ns_list

        setting.template_bucket_name = f'''{full_domain_name.replace(".","-")}-{str(setting.deployment_type.value)}-{str(
            uuid.uuid3(uuid.NAMESPACE_DNS, full_domain_name)
        )}'''

        gateways.deployment_settings.create_or_update(setting)

        root_domain = '.'.join(full_domain_name.split('.')[1:])

        print(
            BLUE +
            f"Please set up the following DNS record manually for {root_domain}:\n" +
            "\tRecord type: NS\n" +
            "\tTTL: 300\n" +
            "\tValues: (each a separate line)\n" +
            BOLD +
            "\n".join([f"\t\t{n}" for n in ns_list]) +
            f"\n\nIf the DNS provider does't support multi-line values then it has to be {len(ns_list)} separate NS records.\n\n" +
            NEUTRAL
        )
        input('Press ENTER if acknowledged.')
        print(GREEN + 'Done.\n')
