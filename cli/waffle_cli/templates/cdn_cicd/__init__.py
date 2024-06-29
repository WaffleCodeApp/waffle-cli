from troposphere import Template  # pyright: ignore[reportMissingTypeStubs]

from .parameters import Parameters
from .conditions import Conditions
from .web_bucket import WebBucket
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .codebuild_project import CodebuildProject
from .codepipeline import CodePipeline
from .artifacts_bucket_policy import ArtifactsBucketPolicy
from .logging_bucket import LoggingBucket
from .distribution import Distribution
from .routes import Routes


def generate_cdn_cicd_stack_json() -> str:
    t = Template()
    params = Parameters(t)
    conditions = Conditions(t, params)
    web_bucket = WebBucket(t)
    artifacts_bucket = ArtifactsBucket(t)
    cicd_roles = CicdRoles(t, params, artifacts_bucket, web_bucket)
    CodebuildProject(t, params, conditions, cicd_roles)
    CodePipeline(t, params, cicd_roles, conditions, web_bucket, artifacts_bucket)
    ArtifactsBucketPolicy(t, artifacts_bucket, cicd_roles)
    logging_bucket = LoggingBucket(t)
    distribution = Distribution(t, conditions, params, logging_bucket, web_bucket)
    Routes(t, params, distribution)

    return t.to_json()


def generate_cdn_cicd_parameter_list(
    deployment_id: str,
    pipeline_id: str,
    cicd_manual_approval: bool,
    full_domain_name: str,
    web_subdomain: str,
    generic_certificate_arn: str,
    alt_full_domain_name: str | None,
    alt_certificate_arn: str | None,
    github_owner: str,
    github_repo_name: str,
    github_branch: str,
    buildspec_path: str,
    commit_id: str | None = None,
    github_secret_arn: str | None = None,
    api_protocol: str | None = None,
    api_host: str | None = None,
    api_stage: str | None = None,
    user_pool_ref: str | None = None,
    auth_web_client: str | None = None,
    identity_pool_ref: str | None = None,
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
            "ParameterValue": full_domain_name,
        },
        {
            "ParameterKey": "WebHostname",
            "ParameterValue": web_subdomain,
        },
        {
            "ParameterKey": "GenericCertificateArn",
            "ParameterValue": generic_certificate_arn,
        },
        {
            "ParameterKey": "AltFullDomainName",
            "ParameterValue": alt_full_domain_name or "",
        },
        {
            "ParameterKey": "AltCertificateArn",
            "ParameterValue": alt_certificate_arn or "",
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
            "ParameterKey": "AuthUserPoolClientWebRef",
            "ParameterValue": auth_web_client or "",
        },
        {
            "ParameterKey": "AuthIdentityPoolRef",
            "ParameterValue": identity_pool_ref or "",
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
