from argparse import ArgumentParser
from typing import Any

from application_logic.entities.deployment_setting import DeploymentSetting
from application_logic.entities.stack_settings.github_stack_setting import GithubStackSetting
from application_logic.entities.stack_type import StackType
from application_logic.gateway_interfaces import Gateways
from gateways import gateway_implementations
from templates.github import generate_github_parameter_list, generate_github_stack_json
from .command_type import Command


class DeployGithub(Command):
    name: str = "deploy_github"
    description: str = (
        "Generate a CFN template for accessing repositories from GitHub for CICD. "
        "This stack installs a secret that holds the github credentials. "
        "This secret is used by CodePipeline components of other stacks."
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

        github_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=setting.template_bucket_name,
            aws_region=setting.aws_region,
            key="github-template.json",
            content=generate_github_stack_json(),
        )

        if setting.github_stack_setting is None:
            setting.github_stack_setting = GithubStackSetting(
            )

        
        gateways.deployment_settings.create_or_update(setting)

        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=github_template_url,
            setting=setting,
            parameters=generate_github_parameter_list(
                deployment_id=setting.deployment_id,
            ),
            stack_type=StackType.github,
        )

        setting.github_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)
