from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    codebuild,
    Template,
)
from .parameters import Parameters
from .conditions import Conditions
from .cicd_roles import CicdRoles


class CodebuildProject:
    def __init__(self, t: Template, p: Parameters, c: Conditions, cr: CicdRoles):
        t.add_resource(
            codebuild.Project(
                "Project",
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
                        # passing buildtime ARG vars to the Dockerfile
                        codebuild.EnvironmentVariable(
                            Name="AWS_DEFAULT_REGION", Value=Ref("AWS::Region")
                        ),
                        codebuild.EnvironmentVariable(Name="REACT_APP_JSON", Value=""),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_BACKEND_PROTOCOL",
                            # Value="https://",
                            Value=If(
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
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_BACKEND_HOST",
                            # Value = Join("", [Ref(p.api_subdomain), ".", Ref(p.full_domain_name)],),
                            Value=If(
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
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_BACKEND_PATH",
                            # Value="/Prod",
                            Value=If(
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
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_AWS_PROJECT_REGION",
                            Value=Ref("AWS::Region"),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_AWS_COGNITO_IDENTITY_POOL_ID",
                            # Value=Ref(p.identity_pool_ref),
                            Value=If(
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
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_AWS_COGNITO_REGION",
                            # NOTE: Cognito might be moved to a different region on the long-term
                            Value=Ref("AWS::Region"),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_AWS_USER_POOLS_ID",
                            Value=If(
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
                        ),
                        codebuild.EnvironmentVariable(
                            Name="REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID",
                            Value=If(
                                c.custom_auth_web_client,
                                Ref(p.auth_web_client),
                                If(
                                    c.create_userpool_selected,
                                    ImportValue(
                                        Join(
                                            "",
                                            [
                                                Ref(p.deployment_id),
                                                "-AuthUserPoolClientWebRef",
                                            ],
                                        )
                                    ),
                                    "",
                                ),
                            ),
                        ),
                        codebuild.EnvironmentVariable(
                            Name="BUILD_ENV_VARS_JSON", Value=Ref(p.build_env_vars_json)
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
                    BuildSpec=Ref(p.buildspec_path), Type="CODEPIPELINE"
                ),
                SourceVersion=Ref(p.commit_id),
                TimeoutInMinutes=15,
            )
        )
