from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .secret import Secret
from .security_groups import SecurityGroups
from .roles import Roles
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .artifacts_bucket_policy import ArtifactsBucketPolicy
from .ecr_repositoty import EcrRepositoty
from .cicd_security_groups import CicdSecurityGroups
from .alb import Alb
from .alb_alarms import AlbAlarms
from .logging_group import LoggingGroup
from .codebuild_project import CodebuildProject
from .ecs_task import EcsTask
from .ecs_service import EcsService
from .codepipeline import CodePipeline
from .vpc_link import VpcLink
from .apigateway_endpoint import ApiGatewayEndpoint
from .outputs import Outputs


def generate_ecs_cicd_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    secret = Secret(t, params)
    security_groups = SecurityGroups(t, params, conditions)
    roles = Roles(t, params, conditions, secret)

    artifacts_bucket = ArtifactsBucket(t)
    cicd_roles = CicdRoles(t, params, artifacts_bucket)
    ArtifactsBucketPolicy(t, artifacts_bucket, cicd_roles)
    ecr_repositoty = EcrRepositoty(t, cicd_roles)
    cicd_security_groups = CicdSecurityGroups(t, params, conditions, security_groups)
    alb = Alb(t, params, conditions, cicd_security_groups)
    AlbAlarms(t, params, conditions, alb)
    logging_group = LoggingGroup(t, params)
    CodebuildProject(t, params, conditions, ecr_repositoty, secret, cicd_roles)
    ecs_task = EcsTask(
        t, params, conditions, roles, cicd_roles, ecr_repositoty, secret, logging_group
    )
    ecs_service = EcsService(
        t, params, conditions, ecr_repositoty, alb, cicd_security_groups, ecs_task
    )
    CodePipeline(t, params, conditions, artifacts_bucket, cicd_roles, ecs_service)
    vpc_link = VpcLink(t, params, conditions, alb, cicd_security_groups)
    ApiGatewayEndpoint(t, params, conditions, vpc_link, alb)
    Outputs(t, params, alb)

    return t.to_json()


def generate_ecs_parameter_list(
    deployment_id: str,
    pipeline_id: str,
    cicd_manual_approval: bool,
    instance_count: int,
    github_owner: str,
    github_repo_name: str,
    github_branch: str,
    buildspec_path: str,
    vpc_ref: str | None = None,
    vpc_cidr_block: str | None = None,
    primary_private_subnet_ref: str | None = None,
    secondary_private_subnet_ref: str | None = None,
    local_outgoing_connection_security_group_id: str | None = None,
    nat_outgoing_connection_security_group_id: str | None = None,
    ecr_incoming_connection_security_group_id: str | None = None,
    commit_id: str | None = None,
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
) -> list[dict[str, str]]:
    return [
        {
            "ParameterKey": "DeploymentId",
            "ParameterValue": deployment_id,
        },
        {
            "ParameterKey": "PipelineId",
            "ParameterValue": pipeline_id,
        },
        {
            "ParameterKey": "CICDManualApproval",
            "ParameterValue": "True" if cicd_manual_approval else "False",
        },
        {
            "ParameterKey": "InstanceCount",
            "ParameterValue": f"{instance_count}",
        },
        {
            "ParameterKey": "VPCRef",
            "ParameterValue": vpc_ref or "",
        },
        {
            "ParameterKey": "VPCCidrBlock",
            "ParameterValue": vpc_cidr_block or "",
        },
        {
            "ParameterKey": "PrimaryPrivateSubnetRef",
            "ParameterValue": primary_private_subnet_ref or "",
        },
        {
            "ParameterKey": "SecondaryPrivateSubnetRef",
            "ParameterValue": secondary_private_subnet_ref or "",
        },
        {
            "ParameterKey": "LocalOutgoingConnectionSecurityGroupId",
            "ParameterValue": local_outgoing_connection_security_group_id or "",
        },
        {
            "ParameterKey": "NatOutgoingConnectionSecurityGroupId",
            "ParameterValue": nat_outgoing_connection_security_group_id or "",
        },
        {
            "ParameterKey": "EcrIncomingConnectionSecurityGroupId",
            "ParameterValue": ecr_incoming_connection_security_group_id or "",
        },
        {
            "ParameterKey": "GithubOwner",
            "ParameterValue": github_owner,
        },
        {
            "ParameterKey": "GithubRepoName",
            "ParameterValue": github_repo_name,
        },
        {
            "ParameterKey": "GithubBranch",
            "ParameterValue": github_branch,
        },
        {
            "ParameterKey": "CommitID",
            "ParameterValue": commit_id or "",
        },
        {
            "ParameterKey": "BuildspecPath",
            "ParameterValue": buildspec_path,
        },
        {
            "ParameterKey": "GithubSecretArn",
            "ParameterValue": github_secret_arn or "",
        },
        {
            "ParameterKey": "AuthUserPoolArn",
            "ParameterValue": user_pool_arn or "",
        },
        {
            "ParameterKey": "RestApiId",
            "ParameterValue": restapi_id or "",
        },
        {
            "ParameterKey": "RootResourceId",
            "ParameterValue": root_resource_id or "",
        },
        {
            "ParameterKey": "AlertsSnsTopicRef",
            "ParameterValue": alerts_sns_ref or "",
        },
        {
            "ParameterKey": "DeploymentSecretArn",
            "ParameterValue": deployment_secret_arn or "",
        },
        {
            "ParameterKey": "RuntimeJson",
            "ParameterValue": runtime_json or "",
        },
        {
            "ParameterKey": "BuildEnvVarsJson",
            "ParameterValue": build_env_vars_json or "",
        },
        {
            "ParameterKey": "EcsTaskCPU",
            "ParameterValue": ecs_task_cpu or "",
        },
        {
            "ParameterKey": "EcsTaskRAM",
            "ParameterValue": ecs_task_ram or "",
        },
    ]
