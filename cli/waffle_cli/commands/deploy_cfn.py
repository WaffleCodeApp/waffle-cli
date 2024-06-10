from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.cfn_stack_state import CfnStackState
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.cfn_cicd import (
    generate_cfn_cicd_stack_json,
    generate_cfn_cicd_parameter_list,
)
from ..utils.std_colors import BLUE, NEUTRAL, RED
from .command_type import Command
from .deploy_auth_userpool import STACK_ID as AUTH_USERPOOL_STACK_ID
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-cicd-cfn"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployCfn(Command):
    name: str = "deploy_cdn"
    description: str = (
        "Generate a CFN template deploying CFN templates and deploy it to the selected deployment. "
        "The stack deploys a CICD with CodePipeline and CodeBuild, and uses CloudFormation to deploy resources."
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
            "pipeline_id",
            help="An ID that will represent the CICD pipeline. Recommended to use a human-understanable name "
            "that explains the purpose, like for example 'frontend' or 'adminui'.",
        )
        parser.add_argument(
            "--cicd_manual_approval",
            help="Whether a manual approval step is included in the CICD pipeline before deployment.",
            choices=["Yes", "No"],
        )
        parser.add_argument(
            "--github_owner",
            help="GitHub user or organization name that owns the repository to be deployed.",
            required=True,
        )
        parser.add_argument(
            "--github_repo_name",
            help="The name of the repository on GitHub to be deployed.",
            required=True,
        )
        parser.add_argument(
            "--github_branch",
            help="The branch of the repository to be deployed to the chosen deployment.",
            required=True,
        )
        parser.add_argument(
            "--buildspec_path",
            help="Filename with path to the build specification file for CodeBuild in the repo. "
            "Typically 'buildspec.yml' or 'MyProjectSubfolder/buildspec.yml' .",
            required=True,
        )
        parser.add_argument(
            "--full_domain_name",
            help="The domain name of the deployment. For example dev.example.com.",
        )
        parser.add_argument(
            "--api_subdomain",
            help="Subdomain of the api. For example the 'api' from api.dev.example.com ",
            default="api",
        )
        parser.add_argument(
            "--vpc_ref",
            help="Optional. If unspecified, the waffle-default VPC's resources will be used. ",
            default="api",
        )
        parser.add_argument(
            "--primary_private_subnet_ref",
            help="Optional. If unspecified, the waffle-default VPC's resources will be used. ",
        )
        parser.add_argument(
            "--secondary_private_subnet_ref",
            help="Optional. If unspecified, the waffle-default VPC's resources will be used. ",
        )
        parser.add_argument(
            "--local_outgoing_connection_security_group_id",
            help="Optional. If unspecified, the waffle-default VPC's resources will be used. ",
        )
        parser.add_argument(
            "--nat_outgoing_connection_security_group_id",
            help="Optional. If unspecified, the waffle-default VPC's resources will be used. ",
        )
        parser.add_argument(
            "--restapi_id",
            help="Optional. If unspecified, the waffle-default API Gateways's resources will be used. ",
        )
        parser.add_argument(
            "--root_resource_id",
            help="Optional. If unspecified, the waffle-default API Gateways's resources will be used. ",
        )
        parser.add_argument(
            "--commit_id",
            help="If it's not always the latest commit that has to be deployed, then the id of the specific commit.",
            required=False,
        )
        parser.add_argument(
            "--commit_id",
            help="If it's not always the latest commit that has to be deployed, then the id of the specific commit.",
            required=False,
        )
        parser.add_argument(
            "--api_protocol",
            help="If omitted then the waffle api gateway's data will be used.",
            required=False,
        )
        parser.add_argument(
            "--api_host",
            help="If omitted then the waffle api gateway's data will be used.",
            required=False,
        )
        parser.add_argument(
            "--api_stage",
            help="If omitted then the waffle api gateway's data will be used.",
            required=False,
        )
        parser.add_argument(
            "--user_pool_ref",
            help="If omitted then the waffle authentication resources will be used.",
            required=False,
        )
        parser.add_argument(
            "--user_pool_arn",
            help="If omitted then the waffle authentication resources will be used.",
            required=False,
        )
        parser.add_argument(
            "--identity_pool_ref",
            help="If omitted then the waffle authentication resources will be used.",
            required=False,
        )
        parser.add_argument(
            "--alerts_sns_ref",
            help="If omitted then the waffle alerts stack's resources will be used.",
            required=False,
        )
        parser.add_argument(
            "--build_env_vars_json",
            help="A json string to be passed to the build script as an environmental variable.",
            required=False,
        )
        parser.add_argument(
            "--custom_template_name",
            help="Optional. If there is a custom, already uploaded template for this purpose, specify its name.",
        )

    @staticmethod
    def execute(
        deployment_id: str | None = None,
        pipeline_id: str | None = None,
        cicd_manual_approval: str | None = None,
        github_owner: str | None = None,
        github_repo_name: str | None = None,
        github_branch: str | None = None,
        buildspec_path: str | None = None,
        full_domain_name: str | None = None,
        api_subdomain: str | None = None,
        vpc_ref: str | None = None,
        primary_private_subnet_ref: str | None = None,
        secondary_private_subnet_ref: str | None = None,
        local_outgoing_connection_security_group_id: str | None = None,
        nat_outgoing_connection_security_group_id: str | None = None,
        restapi_id: str | None = None,
        root_resource_id: str | None = None,
        commit_id: str | None = None,
        github_secret_arn: str | None = None,
        api_protocol: str | None = None,
        api_host: str | None = None,
        api_stage: str | None = None,
        user_pool_ref: str | None = None,
        user_pool_arn: str | None = None,
        identity_pool_ref: str | None = None,
        alerts_sns_ref: str | None = None,
        deployment_secret_arn: str | None = None,
        build_env_vars_json: str | None = None,
        custom_template_name: str | None = None,
        gateways: Gateways = gateway_implementations,
        **_: Any,
    ) -> None:
        assert deployment_id is not None
        assert pipeline_id is not None
        assert github_owner is not None
        assert github_repo_name is not None
        assert github_branch is not None
        assert buildspec_path is not None

        stack_id = f"{STACK_ID}-{pipeline_id}"

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

        deployment_state: DeploymentState = gateways.deployment_states.get(
            deployment_id
        ) or DeploymentState(deployment_id=deployment_id)

        print(
            "\n\n"
            + BLUE
            + "Deploying static fileserving (web frontend)."
            + NEUTRAL
            + "\n\n"
        )

        require_manual_cicd_approval = (
            deployment_setting.default_require_manual_cicd_approval
            if cicd_manual_approval is None
            else cicd_manual_approval.lower() == "Yes"
        )

        full_domain_name = (
            deployment_setting.full_domain_name
            if full_domain_name is None
            else full_domain_name
        )

        if full_domain_name is None:
            print(
                "\n\n"
                + RED
                + "A full domain name has to be either created for the deplyoment or specified with the full_domain_name parameter."
                + NEUTRAL
            )
            raise Exception("full_domain_name is None")

        api_subdomain = "" if api_subdomain is None else api_subdomain

        commit_id = commit_id if commit_id is not None and commit_id != "" else None

        github_secret_arn = (
            github_secret_arn
            if github_secret_arn is not None and github_secret_arn != ""
            else None
        )

        auth_stack: CfnStackState | None = next(
            (
                stack
                for stack in deployment_state.stacks
                if stack.stack_id == AUTH_USERPOOL_STACK_ID
            ),
            None,
        )
        has_auth_stack = auth_stack is not None

        user_pool_ref = (
            user_pool_ref if user_pool_ref != "" else ("" if has_auth_stack else "*")
        )
        user_pool_arn = (
            user_pool_arn if user_pool_arn != "" else ("" if has_auth_stack else "*")
        )
        identity_pool_ref = (
            identity_pool_ref
            if identity_pool_ref != ""
            else ("" if has_auth_stack else "*")
        )

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=stack_id,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=(
                generate_cfn_cicd_stack_json if custom_template_name is None else None
            ),
            parameter_list=generate_cfn_cicd_parameter_list(
                deployment_id=deployment_id,
                pipeline_id=pipeline_id,
                cicd_manual_approval=require_manual_cicd_approval,
                github_owner=github_owner,
                github_repo_name=github_repo_name,
                github_branch=github_branch,
                buildspec_path=buildspec_path,
                full_domain_name=full_domain_name,
                api_subdomain=api_subdomain,
                vpc_ref=vpc_ref if vpc_ref != "" else None,
                primary_private_subnet_ref=(
                    primary_private_subnet_ref
                    if primary_private_subnet_ref != ""
                    else None
                ),
                secondary_private_subnet_ref=(
                    secondary_private_subnet_ref
                    if secondary_private_subnet_ref != ""
                    else None
                ),
                local_outgoing_connection_security_group_id=(
                    local_outgoing_connection_security_group_id
                    if local_outgoing_connection_security_group_id != ""
                    else None
                ),
                nat_outgoing_connection_security_group_id=(
                    nat_outgoing_connection_security_group_id
                    if nat_outgoing_connection_security_group_id != ""
                    else None
                ),
                restapi_id=restapi_id if restapi_id != "" else None,
                root_resource_id=root_resource_id if root_resource_id != "" else None,
                commit_id=commit_id,
                github_secret_arn=github_secret_arn,
                api_protocol=api_protocol if api_protocol != "" else None,
                api_host=api_host if api_host != "" else None,
                api_stage=api_stage if api_stage != "" else None,
                user_pool_ref=user_pool_ref,
                user_pool_arn=user_pool_arn,
                identity_pool_ref=identity_pool_ref,
                alerts_sns_ref=alerts_sns_ref if alerts_sns_ref != "" else None,
                deployment_secret_arn=(
                    deployment_secret_arn if deployment_secret_arn != "" else None
                ),
                build_env_vars_json=build_env_vars_json or "{}",
            ),
            stack_type=StackType.cdn_cicd,
            include_in_the_project=True,
        )
