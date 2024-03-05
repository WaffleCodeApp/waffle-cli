from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]
from application_logic.entities.deployment_type import DeploymentType


class Parameters:
    deployment_id: Parameter
    deployment_type: Parameter
    pipeline_id: Parameter
    manual_approval: Parameter
    full_domain_name: Parameter
    api_subdomain: Parameter
    vpc_ref: Parameter
    primary_private_subnet_ref: Parameter
    secondary_private_subnet_ref: Parameter
    local_outgoing_connection_security_group_id: Parameter
    nat_outgoing_connection_security_group_id: Parameter
    restapi_id: Parameter
    root_resource_id: Parameter
    github_owner: Parameter
    github_repo_name: Parameter
    github_branch: Parameter
    commit_id: Parameter
    buildspec_path: Parameter
    api_protocol: Parameter
    api_host: Parameter
    api_stage: Parameter
    user_pool_ref: Parameter
    user_pool_arn: Parameter
    identity_pool_ref: Parameter

    alerts_sns_ref: Parameter
    deployment_secret_arn: Parameter
    github_secret_arn: Parameter

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
                Description="(optional) like dev.wafflecode.app",
                Type="String",
                Default="",
            )
        )

        self.api_subdomain = t.add_parameter(
            Parameter(
                "BackendApiHostname",
                Description="(optional) api from api.dev.example.com",
                Type="String",
                Default="",
            )
        )

        self.vpc_ref = t.add_parameter(
            Parameter(
                "VPCRef", Description="(optional) The VPC", Type="String", Default=""
            )
        )

        self.primary_private_subnet_ref = t.add_parameter(
            Parameter(
                "PrimaryPrivateSubnetRef",
                Description="(optional) The primary private subnet in the VPC",
                Type="String",
                Default="",
            )
        )

        self.secondary_private_subnet_ref = t.add_parameter(
            Parameter(
                "SecondaryPrivateSubnetRef",
                Description="(optional) The secondary private subnet in the VPC",
                Type="String",
                Default="",
            )
        )

        self.local_outgoing_connection_security_group_id = t.add_parameter(
            Parameter(
                "LocalOutgoingConnectionSecurityGroupId",
                Description="(optional) Local outbound enabled SG",
                Type="String",
                Default="",
            )
        )

        self.nat_outgoing_connection_security_group_id = t.add_parameter(
            Parameter(
                "NatOutgoingConnectionSecurityGroupId",
                Description="(optional) NAT outbound enabled SG",
                Type="String",
                Default="",
            )
        )

        self.restapi_id = t.add_parameter(
            Parameter(
                "RestApiId",
                Description="(optional) The ref of the API Gateway to deploy to",
                Type="String",
                Default="",
            )
        )

        self.root_resource_id = t.add_parameter(
            Parameter(
                "RootResourceId",
                Description="(optional) The ID of the API GW resource to deploy the new"
                "resources as children",
                Type="String",
                Default="",
            )
        )

        self.github_owner = t.add_parameter(
            Parameter("GithubOwner", Description="Github account name", Type="String")
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
                Description="(optional) GitHub commit ID of that has to be built",
                Type="String",
                Default="",
            )
        )

        self.buildspec_path = t.add_parameter(
            Parameter(
                "BuildspecPath",
                Description="Path with filename to the buildspec.yml for CodeBuild",
                Type="String",
                Default="",
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

        self.user_pool_arn = t.add_parameter(
            Parameter(
                "AuthUserPoolArn",
                Description="(optional) The ARN of the user pool",
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

        self.alerts_sns_ref = t.add_parameter(
            Parameter(
                "AlertsSnsTopicRef",
                Description="(optional) The ref of the sns topic to deliver alarms",
                Type="String",
                Default="",
            )
        )

        self.deployment_secret_arn = t.add_parameter(
            Parameter(
                "DeploymentSecretArn",
                Description="(optional) The arn of the deployment_secret",
                Type="String",
                Default="",
            )
        )

        self.github_secret_arn = t.add_parameter(
            Parameter(
                "GithubSecretArn",
                Description="(optional) The arn of the github_secret",
                Type="String",
                Default="",
            )
        )
