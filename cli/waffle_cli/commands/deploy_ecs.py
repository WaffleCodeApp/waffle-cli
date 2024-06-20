from argparse import ArgumentParser
from typing import Any

from templates.ecs_cicd import generate_ecs_cicd_stack_json, generate_ecs_parameter_list

from ..application_logic.entities.cfn_stack_state import CfnStackState
from ..application_logic.entities.deployment_setting import DeploymentSetting
from ..application_logic.entities.deployment_state import DeploymentState
from ..application_logic.entities.stack_type import StackType
from ..application_logic.gateway_interfaces import Gateways
from ..gateways import gateway_implementations
from ..utils.std_colors import NEUTRAL, RED
from .command_type import Command
from .deploy_auth_userpool import STACK_ID as AUTH_USERPOOL_STACK_ID
from .utils.deploy_new_stack import deploy_new_stack

STACK_ID = "waffle-cicd-ecs"
TEMPLATE_NAME = f"{STACK_ID}.json"


class DeployEcs(Command):
    name: str = "deploy_ecs"
    description: str = (
        "Generate a CFN template for running a containerized backend service and deploy it to the selected deployment. "
        "The stack deploys a CICD with CodePipeline and CodeBuild, and uses ECR and ECS Fargate with API Gateway HTTP REST resources to provide the service."
    )

    @staticmethod
    def arg_parser(
        parser: ArgumentParser, gateways: Gateways = gateway_implementations
    ) -> None:
        parser.add_argument(
            "deployment_id",
            help="The ID of an existing Waffle deployment to deploy into.",
            choices=gateways.deployment_settings.get_names(),
        )
        parser.add_argument(
            "pipeline_id",
            help="An ID that will represent the CICD pipeline. Recommended to use a human-understanable name "
            "that explains the purpose, like for example 'frontend' or 'adminui'.",
        )
        parser.add_argument(
            "--cicd_manual_approval",
            help="Optional. Whether a manual approval step is included in the CICD pipeline before deployment.",
            choices=["Yes", "No"],
        )
        parser.add_argument(
            "--instance_count",
            help="Number of desired instances running in paraallel.",
            required=True,
        )
        parser.add_argument(
            "--vpc_ref",
            help="Optional. The REF of the VPC to deploy to",
        )
        parser.add_argument(
            "--vpc_cidr_block",
            help="Optional. The VPC's CIDR block (IP mask)",
        )
        parser.add_argument(
            "--primary_private_subnet_ref",
            help="Optional. The primary private subnet in the VPC",
        )
        parser.add_argument(
            "--secondary_private_subnet_ref",
            help="Optional. The secondary private subnet in the VPC",
        )
        parser.add_argument(
            "--local_outgoing_connection_security_group_id",
            help="Optional. Local outbound traffic enabling Security Group"
            "Required if alt_full_domain_name specified.",
        )
        parser.add_argument(
            "--nat_outgoing_connection_security_group_id",
            help="Optional. NAT outbound traffic enabling Security Group",
            required=True,
        )
        parser.add_argument(
            "--ecr_incoming_connection_security_group_id",
            help="Optional. Network traffic to ECR enabling Security Group",
            required=True,
        )
        parser.add_argument(
            "--github_owner",
            help="The account name of the GitHub repository to be deployed to the chosen deployment.",
            required=True,
        )
        parser.add_argument(
            "--github_repo_name",
            help="The name of the GitHub repository to be deployed to the chosen deployment.",
            required=True,
        )
        parser.add_argument(
            "--github_branch",
            help="The branch of the repository to be deployed to the chosen deployment.",
            required=True,
        )
        parser.add_argument(
            "--commit_id",
            help="Optional. If it's not always the latest commit that has to be deployed, then the id of the specific commit.",
            required=False,
        )
        parser.add_argument(
            "--buildspec_path",
            help="Filename with path to the build specification file for CodeBuild in the repo. "
            "Typically 'buildspec.yml' or 'MyProjectSubfolder/buildspec.yml' .",
            required=True,
        )
        parser.add_argument(
            "--github_secret_arn",
            help="Optional. The arn of the secret with the GitHub credentials to be used with the CICD webhooks.",
            required=False,
        )
        parser.add_argument(
            "--user_pool_arn",
            help="Optional. The ARN of the user pool.",
            required=False,
        )
        parser.add_argument(
            "--restapi_id",
            help="Optional. The REF of the API Gateway to deploy to",
            required=False,
        )
        parser.add_argument(
            "--root_resource_id",
            help="Optional. The ID of the API GW resource to deploy the new HTTP endpoint resources as children",
            required=False,
        )
        parser.add_argument(
            "--alerts_sns_ref",
            help="Optional. The REF of the SNS Topic to send alarms to",
            required=False,
        )
        parser.add_argument(
            "--deployment_secret_arn",
            help="Optional. The ARN of the deployment specific secret",
            required=False,
        )
        parser.add_argument(
            "--runtime_json",
            help="Optional. A stringified JSON that will be passed to the running instance as an environmental variable",
            required=False,
        )
        parser.add_argument(
            "--build_env_vars_json",
            help="Optional. A JSON string to be passed to the build script as an environmental variable.",
            required=False,
        )
        parser.add_argument(
            "--ecs_task_cpu",
            help="Optional. CPU capacity of a single deployed instance (for example 256 or 1024)",
        )
        parser.add_argument(
            "--ecs_task_ram",
            help="Optional. RAM capacity of a single deployed instance (for example 512 or 3072)",
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
        instance_count: str | None = None,
        vpc_ref: str | None = None,
        vpc_cidr_block: str | None = None,
        primary_private_subnet_ref: str | None = None,
        secondary_private_subnet_ref: str | None = None,
        local_outgoing_connection_security_group_id: str | None = None,
        nat_outgoing_connection_security_group_id: str | None = None,
        ecr_incoming_connection_security_group_id: str | None = None,
        github_owner: str | None = None,
        github_repo_name: str | None = None,
        github_branch: str | None = None,
        commit_id: str | None = None,
        buildspec_path: str | None = None,
        github_secret_arn: str | None = None,
        user_pool_arn: str | None = None,
        restapi_id: str | None = None,
        root_resource_id: str | None = None,
        alerts_sns_ref: str | None = None,
        deployment_secret_arn: str | None = None,
        runtime_json: str | None = None,
        build_env_vars_json: str | None = None,
        ecs_task_cpu: str | None = None,
        ecs_task_ram: str | None = None,
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
        assert instance_count is not None

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

        require_manual_cicd_approval = (
            deployment_setting.default_require_manual_cicd_approval
            if cicd_manual_approval is None
            else cicd_manual_approval.lower() == "Yes"
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

        user_pool_arn = (
            user_pool_arn if user_pool_arn != "" else ("" if has_auth_stack else "*")
        )

        deploy_new_stack(
            deployment_id=deployment_id,
            stack_id=stack_id,
            template_name=custom_template_name or TEMPLATE_NAME,
            generate_stack_json=(
                generate_ecs_cicd_stack_json if custom_template_name is None else None
            ),
            parameter_list=generate_ecs_parameter_list(
                deployment_id=deployment_id,
                pipeline_id=pipeline_id,
                cicd_manual_approval=require_manual_cicd_approval,
                instance_count=int(instance_count),
                github_owner=github_owner,
                github_repo_name=github_repo_name,
                github_branch=github_branch,
                buildspec_path=buildspec_path,
                vpc_ref=vpc_ref if vpc_ref != "" else None,
                vpc_cidr_block=vpc_cidr_block if vpc_cidr_block != "" else None,
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
                ecr_incoming_connection_security_group_id=(
                    ecr_incoming_connection_security_group_id
                    if ecr_incoming_connection_security_group_id != ""
                    else None
                ),
                commit_id=commit_id if commit_id != "" else None,
                github_secret_arn=(
                    github_secret_arn if github_secret_arn != "" else None
                ),
                user_pool_arn=user_pool_arn if user_pool_arn != "" else None,
                restapi_id=restapi_id if restapi_id != "" else None,
                root_resource_id=root_resource_id if root_resource_id != "" else None,
                alerts_sns_ref=alerts_sns_ref if alerts_sns_ref != "" else None,
                deployment_secret_arn=(
                    deployment_secret_arn if deployment_secret_arn != "" else None
                ),
                runtime_json=runtime_json if runtime_json != "" else None,
                build_env_vars_json=build_env_vars_json or "{}",
                ecs_task_cpu=ecs_task_cpu if ecs_task_cpu != "" else None,
                ecs_task_ram=ecs_task_ram if ecs_task_ram != "" else None,
            ),
            stack_type=StackType.cdn_cicd,
            include_in_the_project=True,
        )
