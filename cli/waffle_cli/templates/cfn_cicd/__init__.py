from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .secret import Secret
from .roles import Roles
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .codebuild_project import CodebuildProject
from .codepipeline import CodePipeline
from .artifacts_bucket_policy import ArtifactsBucketPolicy


def generate_cfn_cicd_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    secret = Secret(t, params)
    roles = Roles(t, params, conditions, secret)
    artifacts_bucket = ArtifactsBucket(t)
    cicd_roles = CicdRoles(t, params, artifacts_bucket)
    CodebuildProject(t, params, conditions, artifacts_bucket, roles, secret, cicd_roles)
    CodePipeline(t, params, conditions, artifacts_bucket, cicd_roles)
    ArtifactsBucketPolicy(t, artifacts_bucket, cicd_roles)

    return t.to_json()


def generate_cfn_cicd_parameter_list(
    deployment_id: str,
    pipeline_id: str,
    cicd_manual_approval: bool,
    github_owner: str,
    github_repo_name: str,
    github_branch: str,
    buildspec_path: str,
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
    log_retention_days: int = 365,
    alarms_enabled: bool = True,
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
            "ParameterKey": "FullDomainName",
            "ParameterValue": full_domain_name or "",
        },
        {
            "ParameterKey": "BackendApiHostname",
            "ParameterValue": api_subdomain or "",
        },
        {
            "ParameterKey": "VPCRef",
            "ParameterValue": vpc_ref or "",
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
            "ParameterKey": "RestApiId",
            "ParameterValue": restapi_id or "",
        },
        {
            "ParameterKey": "RootResourceId",
            "ParameterValue": root_resource_id or "",
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
            "ParameterKey": "ApiProtocol",
            "ParameterValue": api_protocol or "",
        },
        {
            "ParameterKey": "ApiHost",
            "ParameterValue": api_host or "",
        },
        {
            "ParameterKey": "ApiStage",
            "ParameterValue": api_stage or "",
        },
        {
            "ParameterKey": "AuthUserPoolRef",
            "ParameterValue": user_pool_ref or "",
        },
        {
            "ParameterKey": "AuthUserPoolArn",
            "ParameterValue": user_pool_arn or "",
        },
        {
            "ParameterKey": "AuthIdentityPoolRef",
            "ParameterValue": identity_pool_ref or "",
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
            "ParameterKey": "BuildEnvVarsJson",
            "ParameterValue": build_env_vars_json or "",
        },
        {
            "ParameterKey": "LogRetentionDays",
            "ParameterValue": f"{log_retention_days}",
        },
        {
            "ParameterKey": "AlarmsEnabled",
            "ParameterValue": "True" if alarms_enabled else "False",
        },
    ]
