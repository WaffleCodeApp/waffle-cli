from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]
from application_logic.entities.deployment_type import DeploymentType


class Parameters:
    deployment_id: Parameter
    deployment_type: Parameter
    pipeline_id: Parameter
    manual_approval: Parameter
    full_domain_name: Parameter
    web_subdomain: Parameter
    generic_certificate_arn: Parameter
    alt_full_domain_name: Parameter
    alt_certificate_arn: Parameter
    github_owner: Parameter
    github_secret_arn: Parameter
    github_repo_name: Parameter
    github_branch: Parameter
    commit_id: Parameter
    buildspec_path: Parameter
    api_protocol: Parameter
    api_host: Parameter
    api_stage: Parameter
    user_pool_ref: Parameter
    auth_web_client: Parameter
    identity_pool_ref: Parameter

    build_env_vars_json: Parameter

    def __init__(self, t: Template):
        self.deployment_id = t.add_parameter(
            Parameter("DeploymentId", Description="deployment_id", Type="String")
        )

        self.deployment_type = t.add_parameter(
            Parameter(
                "DeploymentType",
                Description="[ %s ]"
                % " | ".join(
                    [
                        DeploymentType.DEV.value,
                        DeploymentType.PROD.value,
                    ]
                ),
                Type="String",
            )
        )

        self.pipeline_id = t.add_parameter(
            Parameter("PipelineId", Description="pipeline_id", Type="String")
        )

        self.manual_approval = t.add_parameter(
            Parameter(
                "CICDManualApproval",
                Description="Is manual approval required before deployment?",
                Type="String",
                AllowedValues=["True", "False"],
                Default="True",
            )
        )

        self.full_domain_name = t.add_parameter(
            Parameter(
                "FullDomainName",
                Description="like dev.wafflecode.app",
                Type="String",
            )
        )

        self.web_subdomain = t.add_parameter(
            Parameter(
                "WebHostname",
                Description="www from www.dev.wafflecode.app",
                Type="String",
                Default="www",
            )
        )

        self.generic_certificate_arn = t.add_parameter(
            Parameter(
                "GenericCertificateArn",
                Description="For the cert for the *.fulldomain",
                Type="String",
            )
        )

        self.alt_full_domain_name = t.add_parameter(
            Parameter(
                "AltFullDomainName",
                Description="(optional) Like somethingelse.com, where the frontend is also to be found",
                Type="String",
                Default="",
            )
        )
        self.alt_certificate_arn = t.add_parameter(
            Parameter(
                "AltCertificateArn",
                Description="(optional) For the cert for the somethingelse.com",
                Type="String",
                Default="",
            )
        )

        self.github_owner = t.add_parameter(
            Parameter("GithubOwner", Description="Github account name", Type="String")
        )

        self.github_secret_arn = t.add_parameter(
            Parameter(
                "GithubSecretArn",
                Description="(optional) The arn of the github_secret",
                Type="String",
                Default="",
            )
        )

        self.github_repo_name = t.add_parameter(
            Parameter(
                "GithubRepoName", Description="GitHub repository name", Type="String"
            )
        )

        self.github_branch = t.add_parameter(
            Parameter(
                "GithubBranch",
                Description="GitHub branch name to be deployed",
                Type="String",
                Default="main",
            )
        )

        self.commit_id = t.add_parameter(
            Parameter(
                "CommitID",
                Description="(optional) GitHub commit ID of that has to be built. If unspecified it always automatically builds the latest.",
                Type="String",
                Default="",
            )
        )

        self.buildspec_path = t.add_parameter(
            Parameter(
                "BuildspecPath",
                Description="Path with filename to the buildspec.yml for CodeBuild",
                Type="String",
            )
        )

        self.api_protocol = t.add_parameter(
            Parameter(
                "ApiProtocol",
                Description="(optional) https://",
                Type="String",
                Default="",
            )
        )

        self.api_host = t.add_parameter(
            Parameter(
                "ApiHost",
                Description="(optional) Hostname of the Api Gateway",
                Type="String",
                Default="",
            )
        )

        self.api_stage = t.add_parameter(
            Parameter(
                "ApiStage",
                Description="(optional) Api Gateway stage path: /Prod",
                Type="String",
                Default="",
            )
        )

        self.user_pool_ref = t.add_parameter(
            Parameter(
                "AuthUserPoolRef",
                Description="(optional) The REF of the user pool",
                Type="String",
                Default="",
            )
        )

        self.auth_web_client = t.add_parameter(
            Parameter(
                "AuthUserPoolClientWebRef",
                Description="(optional) The REF of the user pool web client",
                Type="String",
                Default="",
            )
        )

        self.identity_pool_ref = t.add_parameter(
            Parameter(
                "AuthIdentityPoolRef",
                Description="(optional) The REF of the user pool",
                Type="String",
                Default="",
            )
        )

        self.build_env_vars_json = t.add_parameter(
            Parameter(
                "BuildEnvVarsJson",
                Description="(optional) A JSON that will be used as env var during build. ",
                Type="String",
                Default="{}",
            )
        )
