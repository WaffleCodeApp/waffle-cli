from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    Sub,
    codebuild,
    Template,
)

from .parameters import Parameters
from .conditions import Conditions
from .artifacts_bucket import ArtifactsBucket
from .roles import Roles
from .secret import Secret
from .cicd_roles import CicdRoles


class CodebuildProject:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        ab: ArtifactsBucket,
        r: Roles,
        s: Secret,
        cr: CicdRoles,
    ) -> None:
        t.add_resource(
            codebuild.Project(
                "Project",
                DependsOn="ArtifactsBucket",
                Artifacts=codebuild.Artifacts(
                    Type="CODEPIPELINE",
                ),
                Description=Join(
                    "",
                    [Ref(p.deployment_id), "-", Ref(p.pipeline_id), " build project"],
                ),
                Environment=codebuild.Environment(
                    ComputeType="BUILD_GENERAL1_MEDIUM",
                    # NOTE: this is frequently updated
                    # https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
                    Image="aws/codebuild/standard:7.0",  ## ubuntu 22.04
                    Type="LINUX_CONTAINER",
                    EnvironmentVariables=[
                        # passing buildtime ARG vars to build.yml
                        codebuild.EnvironmentVariable(
                            Name="AWS_DEFAULT_REGION", Value=Ref("AWS::Region")
                        ),
                        codebuild.EnvironmentVariable(
                            Name="S3_BUCKET", Value=Ref(ab.artifacts_bucket)
                        ),
                        codebuild.EnvironmentVariable(
                            Name="DEPLOYMENT_SECRET_ARN",
                            Value=If(
                                c.custom_deployment_secret_arn,
                                Ref(p.deployment_secret_arn),
                                ImportValue(
                                    Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-DeploymentSecretArn",
                                        ],
                                    )
                                ),
                            ),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="SERVICE_SECRET_ARN", Value=Ref(s.secret)
                        ),
                        codebuild.EnvironmentVariable(
                            Name="BUILD_ENV_VARS_JSON", Value="{}"
                        ),
                        codebuild.EnvironmentVariable(
                            Name="JSON",
                            Value=Sub(
                                "{"
                                '"DeploymentId":"${DeploymentId}",'
                                '"PipelineId":"${PipelineId}",'
                                '"RestApiId":"${RestApiId}",'
                                '"RootResourceId":"${RootResourceId}",'
                                '"LambdaExecutionRoleARN":"${LambdaExecutionRoleARN}",'
                                '"CodeDeployServiceRoleARN":"${CodeDeployServiceRoleARN}",'
                                '"LocalOutgoingSecurityGroup":"${LocalOutgoingSecurityGroup}",'
                                '"NATOutgoingSecurityGroup":"${NATOutgoingSecurityGroup}",'
                                '"VPCRef":"${VPCRef}",'
                                '"SubnetPrimary":"${PrimaryPrivateSubnetRef}",'
                                '"SubnetSecondary":"${SecPrivateSubnetRef}",'
                                '"ServiceSecretArn":"${ServiceSecretArn}",'
                                '"ApiProtocol":"${ApiProtocol}",'
                                '"ApiHost":"${ApiHost}",'
                                '"ApiStage":"${ApiStage}",'
                                '"CognitoProjectRegion":"${CognitoProjectRegion}",'
                                '"CognitoRegion":"${CognitoRegion}",'
                                '"UserPoolId":"${UserPoolId}",'
                                '"IdentityPoolId":"${IdentityPoolId}",'
                                '"AlertsTopicRef":"${AlertsTopicRef}",'
                                '"EnvVarsJson":"${EnvVarsJson}"'
                                "}",
                                {
                                    "DeploymentId": Ref(p.deployment_id),
                                    "PipelineId": Ref(p.pipeline_id),
                                    "RestApiId": If(
                                        c.custom_restapi_id,
                                        Ref(p.restapi_id),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-RestApiId",
                                                ],
                                            )
                                        ),
                                    ),
                                    "RootResourceId": If(
                                        c.custom_root_resource_id,
                                        Ref(p.root_resource_id),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-RootResourceId",
                                                ],
                                            )
                                        ),
                                    ),
                                    "LambdaExecutionRoleARN": GetAtt(
                                        r.lambda_execution_role, "Arn"
                                    ),
                                    "CodeDeployServiceRoleARN": GetAtt(
                                        cr.deploy_cfn_changeset_role, "Arn"
                                    ),
                                    "LocalOutgoingSecurityGroup": If(
                                        c.custom_local_outgoing_connections_sg,
                                        Ref(
                                            p.local_outgoing_connection_security_group_id
                                        ),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-LocalOutgoingConnectionSecurityGroupId",
                                                ],
                                            )
                                        ),
                                    ),
                                    "NATOutgoingSecurityGroup": If(
                                        c.custom_nat_outgoing_connections_sg,
                                        Ref(
                                            p.nat_outgoing_connection_security_group_id
                                        ),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-NatOutgoingConnectionSecurityGroupId",
                                                ],
                                            )
                                        ),
                                    ),
                                    "VPCRef": If(
                                        c.custom_vpc_ref,
                                        Ref(p.vpc_ref),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-VPCRef",
                                                ],
                                            )
                                        ),
                                    ),
                                    "PrimaryPrivateSubnetRef": If(
                                        c.custom_primary_private_subnet_ref,
                                        Ref(p.primary_private_subnet_ref),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-PrimaryPrivateSubnetRef",
                                                ],
                                            )
                                        ),
                                    ),
                                    "SecPrivateSubnetRef": If(
                                        c.custom_secondary_private_subnet_ref,
                                        Ref(p.secondary_private_subnet_ref),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-SecondaryPrivateSubnetRef",
                                                ],
                                            )
                                        ),
                                    ),
                                    "ServiceSecretArn": Ref(s.secret),
                                    "ApiProtocol": If(
                                        c.custom_api_protocol,
                                        Ref(p.api_protocol),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-ApiProtocol",
                                                ],
                                            )
                                        ),
                                    ),
                                    "ApiHost": If(
                                        c.custom_api_host,
                                        Ref(p.api_host),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-ApiHost",
                                                ],
                                            )
                                        ),
                                    ),
                                    "ApiStage": If(
                                        c.custom_api_stage,
                                        Ref(p.api_stage),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-ApiStage",
                                                ],
                                            )
                                        ),
                                    ),
                                    "CognitoProjectRegion": Ref("AWS::Region"),
                                    "CognitoRegion": Ref("AWS::Region"),
                                    "UserPoolId": If(
                                        c.custom_user_pool_ref,
                                        Ref(p.user_pool_ref),
                                        If(
                                            c.create_userpool_selected,
                                            ImportValue(
                                                Join(
                                                    "",
                                                    [
                                                        Ref(p.deployment_id),
                                                        "-AuthUserPoolRef",
                                                    ],
                                                )
                                            ),
                                            "",
                                        ),
                                    ),
                                    "IdentityPoolId": If(
                                        c.custom_identity_pool_ref,
                                        Ref(p.identity_pool_ref),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-AuthIdentityPoolRef",
                                                ],
                                            )
                                        ),
                                    ),
                                    "AlertsTopicRef": If(
                                        c.custom_alerts_sns_ref,
                                        Ref(p.alerts_sns_ref),
                                        ImportValue(
                                            Join(
                                                "",
                                                [
                                                    Ref(p.deployment_id),
                                                    "-AlertsSnsTopicRef",
                                                ],
                                            )
                                        ),
                                    ),
                                    "EnvVarsJson": "",
                                },
                            ),
                        ),
                    ],
                ),
                Name=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                    ],
                ),
                ServiceRole=GetAtt(cr.codebuild_role, "Arn"),
                Source=codebuild.Source(
                    Type="CODEPIPELINE", BuildSpec=Ref(p.buildspec_path)
                ),
                SourceVersion=Ref(p.commit_id),
                TimeoutInMinutes=15,
            )
        )
