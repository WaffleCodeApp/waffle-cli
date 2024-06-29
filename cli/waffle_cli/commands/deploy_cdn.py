from argparse import ArgumentParser
from typing import Any

from ..application_logic.entities.cfn_stack_state import CfnStackState
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..templates.cdn_cicd import (
    generate_cdn_cicd_stack_json,
    generate_cdn_cicd_parameter_list,
)
from ..utils.std_colors import BLUE, NEUTRAL, RED
from .command_type import Command
from .deploy_auth_userpool import STACK_ID as AUTH_USERPOOL_STACK_ID
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-cicd-cdn"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployCdn(Command):
    name: str = "deploy_cdn"
    description: str = (
        "Generate a CFN template for serving frontend static files and deploy it to the selected deployment. "
        "The stack deploys a CICD with CodePipeline and CodeBuild, and uses S3 and CloudFront for file-serving."
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
            "--full_domain_name",
            help="The domain name of the deployment. For example dev.example.com.",
        )
        parser.add_argument(
            "--web_subdomain",
            help="Subdomain of the frontend. For example the 'www' from www.dev.example.com ",
            default="www",
        )
        parser.add_argument(
            "--generic_certificate_arn",
            help="Optional. The arn of the generic certificate that can be used for the full domain name and its subdomains. If omitted then the one generated by waffle is being used.",
        )
        parser.add_argument(
            "--alt_full_domain_name",
            help="Optional. A full domain name that you want to use for serving this frontend. Like for example mybrand.app .",
        )
        parser.add_argument(
            "--alt_certificate_arn",
            help="Optional. The ARN of an AWS hosted certificate that can be used for serving the alt_full_domain_name with SSL. "
            "Required if alt_full_domain_name specified.",
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
            "--commit_id",
            help="If it's not always the latest commit that has to be deployed, then the id of the specific commit.",
            required=False,
        )
        parser.add_argument(
            "--buildspec_path",
            help="Filename with path to the build specification file for CodeBuild in the repo. "
            "Typically 'buildspec.yml' or 'MyProjectSubfolder/buildspec.yml' .",
            required=True,
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
            "--auth_web_client",
            help="If omitted then the waffle authentication resources will be used.",
            required=False,
        )
        parser.add_argument(
            "--identity_pool_ref",
            help="If omitted then the waffle authentication resources will be used.",
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
        full_domain_name: str | None = None,
        web_subdomain: str | None = None,
        generic_certificate_arn: str | None = None,
        alt_full_domain_name: str | None = None,
        alt_certificate_arn: str | None = None,
        github_owner: str | None = None,
        github_repo_name: str | None = None,
        github_branch: str | None = None,
        commit_id: str | None = None,
        buildspec_path: str | None = None,
        github_secret_arn: str | None = None,
        api_protocol: str | None = None,
        api_host: str | None = None,
        api_stage: str | None = None,
        user_pool_ref: str | None = None,
        auth_web_client: str | None = None,
        identity_pool_ref: str | None = None,
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

        web_subdomain = "www" if web_subdomain is None else web_subdomain

        generic_certificate_arn = (
            generic_certificate_arn
            if generic_certificate_arn is not None
            else deployment_state.generic_certificate_arn
        )

        if generic_certificate_arn is None:
            print(
                "\n\n"
                + RED
                + "A generic certificate has to be either created for the deplyoment or specified with the generic_certificate_arn parameter."
                + NEUTRAL
            )
            raise Exception("generic certificate arn not found")

        alt_full_domain_name = (
            alt_full_domain_name
            if alt_full_domain_name is not None and alt_full_domain_name != ""
            else None
        )

        alt_certificate_arn = (
            alt_certificate_arn
            if alt_certificate_arn is not None and alt_certificate_arn != ""
            else None
        )

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
        auth_web_client = (
            auth_web_client
            if auth_web_client != ""
            else ("" if has_auth_stack else "*")
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
                generate_cdn_cicd_stack_json if custom_template_name is None else None
            ),
            parameter_list=generate_cdn_cicd_parameter_list(
                deployment_id=deployment_id,
                pipeline_id=pipeline_id,
                cicd_manual_approval=require_manual_cicd_approval,
                full_domain_name=full_domain_name,
                web_subdomain=web_subdomain,
                generic_certificate_arn=generic_certificate_arn,
                alt_full_domain_name=alt_full_domain_name,
                alt_certificate_arn=alt_certificate_arn,
                github_owner=github_owner,
                github_repo_name=github_repo_name,
                github_branch=github_branch,
                commit_id=commit_id,
                buildspec_path=buildspec_path,
                github_secret_arn=github_secret_arn,
                api_protocol=api_protocol if api_protocol != "" else None,
                api_host=api_host if api_host != "" else None,
                api_stage=api_stage if api_stage != "" else None,
                user_pool_ref=user_pool_ref,
                auth_web_client=auth_web_client,
                identity_pool_ref=identity_pool_ref,
                build_env_vars_json=build_env_vars_json or "{}",
            ),
            stack_type=StackType.cdn_cicd,
            include_in_the_project=True,
        )