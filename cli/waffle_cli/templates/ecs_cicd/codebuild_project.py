from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    codebuild,
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions
from .ecr_repositoty import EcrRepositoty
from .secret import Secret
from .cicd_roles import CicdRoles


class CodebuildProject:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        er: EcrRepositoty,
        s: Secret,
        cr: CicdRoles,
    ):
        t.add_resource(
            codebuild.Project(
                "Project",
                Artifacts=codebuild.Artifacts(
                    Type="CODEPIPELINE",
                ),
                Description=Join(
                    "",
                    [
                        Ref(p.deployment_id),
                        "-",
                        Ref(p.pipeline_id),
                        " build project",
                    ],
                ),
                Environment=codebuild.Environment(
                    ComputeType="BUILD_GENERAL1_SMALL",
                    # NOTE: this is frequently updated
                    # https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-available.html
                    Image="aws/codebuild/standard:7.0",  ## ubuntu 22.04
                    Type="LINUX_CONTAINER",
                    PrivilegedMode=True,
                    EnvironmentVariables=[
                        # passing buildtime ARG vars to the Dockerfile
                        codebuild.EnvironmentVariable(
                            Name="AWS_REGION", Value=Ref("AWS::Region")
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REPOSITORY_URI", Value=er.uri
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REPO_NAME", Value=Ref(er.repository)
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
                            Name="ALERTS_TOPIC_ARN",
                            Value=If(
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
                        ),
                        codebuild.EnvironmentVariable(
                            Name="SERVICE_SECRET_ARN",
                            Value=Ref(s.secret),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="RUNTIME_JSON", Value=Ref(p.runtime_json)
                        ),
                        codebuild.EnvironmentVariable(
                            Name="BUILD_ENV_VARS_JSON",
                            Value=Ref(p.build_env_vars_json),
                        ),
                        codebuild.EnvironmentVariable(Name="SERVICE_PORT", Value="80"),
                        codebuild.EnvironmentVariable(
                            Name="DEPLOYMENT_ID",
                            Value=Ref(p.deployment_id),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="DEPLOYMENT_TYPE",
                            Value=Ref(p.deployment_type),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="PIPELINE_ID",
                            Value=Ref(p.pipeline_id),
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
            )
        )
