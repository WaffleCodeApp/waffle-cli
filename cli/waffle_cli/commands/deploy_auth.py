from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.stack_settings.auth_stack_setting import (
    AuthStackSetting,
    AuthType,
)
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.authentication import (
    generate_auth_stack_json,
    generate_auth_parameter_list,
)
from ..utils.std_colors import BLUE, BOLD, GREEN, NEUTRAL, RED
from .command_type import Command


class DeployAuth(Command):
    name: str = "deploy_auth"
    description: str = (
        "Generate a CFN template for authentication and deploy it to the selected deployment. "
        "This stack is required if you want to enable IAM authentication on the API Gateway, "
        "and use it from a frontend application. There are two major options: The first is using Cognito "
        "User Pool, the user authentication service provided by AWS. Alternatively you can select "
        "OIDC authentication, this way an Cognito Identity Pool will still be deployed and used for "
        "IAM authorization on the API Gateway, you can set up an OIDC 3rd party authentication service, "
        "to handle user logins."
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
            "--auth_type",
            help="Only required when run for the first time for a deployment. USERPOOL deploys and AWS Cognito Userpool, while OIDC lets you bring your own authentication service.",
            choices=[t.name for t in AuthType],
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        auth_type: AuthType | None = None,
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

        if setting.template_bucket_name is None:
            print(RED + "Template bucket name setting not found. Please make sure to run configure_deployment_domain first." + NEUTRAL)
            raise Exception("template_bucket_name is None")

        if setting.deployment_type is None:
            print(RED + 'Deployment type setting found. Please make sure to run create_deployment_settings first.' + NEUTRAL)
            raise Exception("Deployment type is None")

        i_auth_type = auth_type
        if setting.auth_stack_setting is None and auth_type is None:
            print(BLUE + BOLD)
            i_auth_type = input("Please specify the authentication type. USERPOOL deploys and AWS Cognito Userpool, while OIDC lets you bring your own authentication service. ")
            if i_auth_type not in AuthType:
                raise Exception("Unknown auth type specified")
            print(NEUTRAL)
        assert i_auth_type is not None

        gateways.deployment_template_bucket.create_bucket_if_not_exist(
            deployment_id, setting.template_bucket_name, setting.aws_region
        )

        auth_template_url: str = gateways.deployment_template_bucket.upload_obj(
            deployment_id=deployment_id,
            bucket_name=setting.template_bucket_name,
            aws_region=setting.aws_region,
            key="auth-template.json",
            content=generate_auth_stack_json(),
        )

        if setting.auth_stack_setting is None:
            setting.auth_stack_setting = AuthStackSetting(
                auth_type=AuthType[i_auth_type],
            )

        gateways.deployment_settings.create_or_update(setting)

        cfn_stack_id = gateways.stacks.create_or_update_stack(
            template_url=auth_template_url,
            setting=setting,
            parameters=generate_auth_parameter_list(
                deployment_id=setting.deployment_id,
                create_userpool=(
                    "True"
                    if setting.auth_stack_setting
                    and setting.auth_stack_setting.auth_type == AuthType.USERPOOL
                    else "False"
                ),
            ),
            stack_type=StackType.auth,
        )

        setting.auth_stack_setting.cfn_stack_id = cfn_stack_id
        gateways.deployment_settings.create_or_update(setting)

        print(GREEN + 'Done. The deployment typically takes a few minutes.\n' + NEUTRAL)
