from argparse import ArgumentParser
from typing import Any

from application_logic.entities.deployment_setting import DeploymentSetting
from application_logic.entities.deployment_type import DeploymentType
from application_logic.entities.stack_settings.vpc_stack_setting import VpcStackSetting
from application_logic.entities.stack_type import StackType
from application_logic.gateway_interfaces import Gateways
from gateways import gateway_implementations
from templates.vpc import generate_vpc_parameter_list, generate_vpc_stack_json
from .command_type import Command


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
        )
        parser.add_argument(
            "--primary_private_cidr",
            help="The CIDR of the primary private subnet. (like for example: 10.51.0.0/19)",
        )
        parser.add_argument(
            "--secondary_private_cidr",
            help="The CIDR of the secondary private subnet. (like for example: 10.51.32.0/19)",
        )
        parser.add_argument(
            "--primary_public_cidr",
            help="The CIDR of the primary public subnet. (like for example: 10.51.128.0/20)",
        )
        parser.add_argument(
            "--secondary_public_cidr",
            help="The CIDR of the secondary public subnet. (like for example: 10.51.144.0/20)",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        vpc_cidr: str | None = None,
        primary_private_cidr: str | None = None,
        secondary_private_cidr: str | None = None,
        primary_public_cidr: str | None = None,
        secondary_public_cidr: str | None = None,
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

        gateways.deployment_template_bucket.create_bucket_if_not_exist(
            deployment_id, setting.template_bucket_name, setting.aws_region
        )

        vpc_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=setting.template_bucket_name,
            aws_region=setting.aws_region,
            key="vpc-template.json",
            content=generate_vpc_stack_json(),
        )

        if [
            vpc_cidr,
            primary_private_cidr,
            secondary_private_cidr,
            primary_public_cidr,
            secondary_public_cidr,
        ].count(None) not in [0, 5]:
            raise Exception("Either all or no custom CIDRs have to be specified")

        if setting.vpc_stack_setting is None:
            if (
                vpc_cidr is not None
                and primary_private_cidr is not None
                and secondary_private_cidr is not None
                and primary_public_cidr is not None
                and secondary_public_cidr is not None
            ):
                setting.vpc_stack_setting = VpcStackSetting(
                    vpc_cidr=vpc_cidr,
                    primary_private_cidr=primary_private_cidr,
                    secondary_private_cidr=secondary_private_cidr,
                    primary_public_cidr=primary_public_cidr,
                    secondary_public_cidr=secondary_public_cidr,
                )
            else:
                match setting.deployment_type:
                    case DeploymentType.DEV:
                        setting.vpc_stack_setting = VpcStackSetting(
                            vpc_cidr="10.51.0.0/16",
                            primary_private_cidr="10.51.0.0/19",
                            secondary_private_cidr="10.51.32.0/19",
                            primary_public_cidr="10.51.128.0/20",
                            secondary_public_cidr="10.51.144.0/20",
                        )
                    case DeploymentType.PROD:
                        setting.vpc_stack_setting = VpcStackSetting(
                            vpc_cidr="10.53.0.0/16",
                            primary_private_cidr="10.53.0.0/19",
                            secondary_private_cidr="10.53.32.0/19",
                            primary_public_cidr="10.53.128.0/20",
                            secondary_public_cidr="10.53.144.0/20",
                        )

        gateways.deployment_settings.create_or_update(setting)

        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=vpc_template_url,
            setting=setting,
            parameters=generate_vpc_parameter_list(
                deployment_id=setting.deployment_id,
                vpc_cidr=setting.vpc_stack_setting.vpc_cidr,
                primary_private_cidr=setting.vpc_stack_setting.primary_private_cidr,
                secondary_private_cidr=setting.vpc_stack_setting.secondary_private_cidr,
                primary_public_cidr=setting.vpc_stack_setting.primary_public_cidr,
                secondary_public_cidr=setting.vpc_stack_setting.secondary_public_cidr,
            ),
            stack_type=StackType.vpc,
        )

        setting.vpc_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)
