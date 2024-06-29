from troposphere import Parameter, Template  # pyright: ignore[reportMissingTypeStubs]


class Parameters:
    deployment_id: Parameter
    pipeline_id: Parameter
    manual_approval: Parameter
    instance_count: Parameter
    vpc_ref: Parameter
    vpc_cidr_block: Parameter
    primary_private_subnet_ref: Parameter
    secondary_private_subnet_ref: Parameter
    local_outgoing_connection_security_group_id: Parameter
    nat_outgoing_connection_security_group_id: Parameter
    ecr_incoming_connection_security_group_id: Parameter
    github_owner: Parameter
    github_repo_name: Parameter
    github_branch: Parameter
    commit_id: Parameter
    buildspec_path: Parameter
    user_pool_arn: Parameter
    restapi_id: Parameter
    root_resource_id: Parameter

    alerts_sns_ref: Parameter
    deployment_secret_arn: Parameter
    github_secret_arn: Parameter

    runtime_json: Parameter
    build_env_vars_json: Parameter

    ecs_task_cpu: Parameter
    ecs_task_ram: Parameter

    def __init__(self, t: Template):
        self.deployment_id = t.add_parameter(
            Parameter(
                "DeploymentId",
                Description="The ID of an existing Waffle deployment to deploy into.",
                Type="String",
            )
        )

        self.pipeline_id = t.add_parameter(
            Parameter(
                "PipelineId",
                Description="An ID that will represent the CICD pipeline. Recommended to use a human-understanable name that explains the purpose, like for example 'frontend' or 'adminui'.",
                Type="String",
            )
        )

        self.manual_approval = t.add_parameter(
            Parameter(
                "CICDManualApproval",
                Description="Whether a manual approval step is included in the CICD pipeline before deployment.",
                Type="String",
                AllowedValues=["True", "False"],
                Default="True",
            )
        )

        self.instance_count = t.add_parameter(
            Parameter(
                "InstanceCount",
                Description="Number of desired instances running in paraallel",
                Type="Number",
                MinValue=0,
            )
        )

        self.vpc_ref = t.add_parameter(
            Parameter(
                "VPCRef",
                Description="(optional) The REF of the VPC to deploy to",
                Type="String",
                Default="",
            )
        )

        self.vpc_cidr_block = t.add_parameter(
            Parameter(
                "VPCCidrBlock",
                Description="(optional) The VPC's CIDR block (IP mask)",
                Type="String",
                Default="",
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
                Description="(optional) Local outbound traffic enabling Security Group",
                Type="String",
                Default="",
            )
        )

        self.nat_outgoing_connection_security_group_id = t.add_parameter(
            Parameter(
                "NatOutgoingConnectionSecurityGroupId",
                Description="(optional) NAT outbound traffic enabling Security Group",
                Type="String",
                Default="",
            )
        )

        self.ecr_incoming_connection_security_group_id = t.add_parameter(
            Parameter(
                "EcrIncomingConnectionSecurityGroupId",
                Description="(optional) Network traffic to ECR enabling Security Group",
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
                Description="(optional) GitHub commit ID of that has to be built.  If unspecified it always automatically builds the latest.",
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

        self.github_secret_arn = t.add_parameter(
            Parameter(
                "GithubSecretArn",
                Description="(optional) The arn of the github_secret",
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
                Description="(optional) The ID of the API GW resource to deploy the new HTTP endpoint resources as children",
                Type="String",
                Default="",
            )
        )

        self.alerts_sns_ref = t.add_parameter(
            Parameter(
                "AlertsSnsTopicRef",
                Description="(optional) The REF of the SNS Topic to send alarms to",
                Type="String",
                Default="",
            )
        )

        self.deployment_secret_arn = t.add_parameter(
            Parameter(
                "DeploymentSecretArn",
                Description="(optional) The ARN of the deployment specific secret",
                Type="String",
                Default="",
            )
        )

        self.runtime_json = t.add_parameter(
            Parameter(
                "RuntimeJson",
                Description="(optional) A JSON that will be passed to the running instance as an environmental variable",
                Type="String",
                Default="{}",
            )
        )

        self.build_env_vars_json = t.add_parameter(
            Parameter(
                "BuildEnvVarsJson",
                Description="(optional) A JSON string to be passed to the build script as an environmental variable.",
                Type="String",
                Default="{}",
            )
        )

        self.ecs_task_cpu = t.add_parameter(
            Parameter(
                "EcsTaskCPU",
                Description="(optional) CPU capacity of a single deployed instance (for example 256 or 1024)",
                Type="String",
                Default="256",
            )
        )

        self.ecs_task_ram = t.add_parameter(
            Parameter(
                "EcsTaskRAM",
                Description="(optional) RAM capacity (for example 512 or 3072)",
                Type="String",
                Default="512",
            )
        )
