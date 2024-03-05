from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    If,
    ImportValue,
    Join,
    Ref,
    codepipeline,
    Template,
)

from .parameters import Parameters
from .conditions import Conditions
from .artifacts_bucket import ArtifactsBucket
from .cicd_roles import CicdRoles
from .ecs_service import EcsService


class CodePipeline:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        ab: ArtifactsBucket,
        cr: CicdRoles,
        es: EcsService,
    ):
        pipeline: codepipeline.Pipeline = t.add_resource(
            codepipeline.Pipeline(
                "Pipeline",
                DependsOn=["Project"],
                RoleArn=GetAtt(cr.codepipeline_role, "Arn"),
                RestartExecutionOnUpdate=True,
                Stages=[
                    codepipeline.Stages(
                        Name="Source",
                        Actions=[
                            codepipeline.Actions(
                                "BuildSourceAction",
                                Name="BuildSourceAction",
                                ActionTypeId=codepipeline.ActionTypeId(
                                    Category="Source",
                                    Owner="ThirdParty",
                                    Version="1",
                                    Provider="GitHub",
                                ),
                                OutputArtifacts=[
                                    codepipeline.OutputArtifacts(Name="SourceArtifact")
                                ],
                                Configuration={
                                    "Owner": Ref(p.github_owner),
                                    "Repo": Ref(p.github_repo_name),
                                    "Branch": Ref(p.github_branch),
                                    "OAuthToken": Join(
                                        "",
                                        [
                                            "{{resolve:secretsmanager:",
                                            If(
                                                c.custom_github_secret_arn,
                                                Ref(p.github_secret_arn),
                                                ImportValue(
                                                    Join(
                                                        "",
                                                        [
                                                            Ref(p.deployment_id),
                                                            "-GithubSecretArn",
                                                        ],
                                                    )
                                                ),
                                            ),
                                            ":SecretString:token}}",
                                        ],
                                    ),
                                    # "OAuthToken": "{{resolve:secretsmanager:arn:aws:secretsmanager:us-east-1:948939170092:secret:GithubSecret-xSqGTe0Uo6La-bZ08hQ:SecretString:token}}",
                                    "PollForSourceChanges": False,
                                },
                                RunOrder=1,
                            )
                        ],
                    ),
                    codepipeline.Stages(
                        Name="Build",
                        Actions=[
                            codepipeline.Actions(
                                "BuildAction",
                                Name="BuildAction",
                                ActionTypeId=codepipeline.ActionTypeId(
                                    Category="Build",
                                    Owner="AWS",
                                    Version="1",
                                    Provider="CodeBuild",
                                ),
                                InputArtifacts=[
                                    codepipeline.InputArtifacts(Name="SourceArtifact")
                                ],
                                OutputArtifacts=[
                                    codepipeline.OutputArtifacts(Name="BuildArtifact")
                                ],
                                Configuration={
                                    "ProjectName": Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-",
                                            Ref(p.pipeline_id),
                                        ],
                                    )
                                },
                                RunOrder=1,
                            )
                        ],
                    ),
                    If(
                        c.manual_approval_selected,
                        codepipeline.Stages(
                            Name="Approval",
                            Actions=[
                                codepipeline.Actions(
                                    "ApprovalAction",
                                    Name="ApprovalAction",
                                    ActionTypeId=codepipeline.ActionTypeId(
                                        Category="Approval",
                                        Owner="AWS",
                                        Version="1",
                                        Provider="Manual",
                                    ),
                                    RunOrder=1,
                                )
                            ],
                        ),
                        Ref("AWS::NoValue"),
                    ),
                    codepipeline.Stages(
                        Name="Deploy",
                        Actions=[
                            codepipeline.Actions(
                                "DeployAction",
                                Name="DeployAction",
                                ActionTypeId=codepipeline.ActionTypeId(
                                    Category="Deploy",
                                    Owner="AWS",
                                    Version="1",
                                    # TODO: configure CICD for Blue/Green
                                    # https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
                                    # I couldn't find any documentation about it on the
                                    # whole internet, so going with simple deployment
                                    # for now.
                                    # Provider="CodeDeployToECS"
                                    Provider="ECS",
                                ),
                                InputArtifacts=[
                                    codepipeline.InputArtifacts(Name="BuildArtifact")
                                ],
                                # This is the config skeleton for Blue/Green setup
                                # As mentioned above there's 0 about it in the docs
                                # Configuration={
                                #    "ApplicationName": "",
                                #    "DeploymentGroupName": "",
                                #    "Image1ArtifactName": "",
                                #    "TaskDefinitionTemplateArtifact": "",
                                #    "Image1ContainerName": "",
                                #    "AppSpecTemplateArtifact": "",
                                #    "AppSpecTemplatePath": "",
                                # },
                                Configuration={
                                    "FileName": "imagedefinitions.json",
                                    "ClusterName": Ref(es.cluster),
                                    "ServiceName": Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-",
                                            Ref(p.pipeline_id),
                                        ],
                                    ),
                                },
                                RunOrder=5,
                            )
                        ],
                    ),
                ],
                ArtifactStore=codepipeline.ArtifactStore(
                    Type="S3", Location=Ref(ab.artifacts_bucket)
                ),
            )
        )

        t.add_resource(
            codepipeline.Webhook(
                "PipelineWebhook",
                Authentication="GITHUB_HMAC",
                AuthenticationConfiguration=codepipeline.WebhookAuthConfiguration(
                    SecretToken=Join(
                        "",
                        [
                            "{{resolve:secretsmanager:",
                            If(
                                c.custom_github_secret_arn,
                                Ref(p.github_secret_arn),
                                ImportValue(
                                    Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-GithubSecretArn",
                                        ],
                                    )
                                ),
                            ),
                            ":SecretString:token}}",
                        ],
                    )
                ),
                Filters=[
                    codepipeline.WebhookFilterRule(
                        JsonPath="$.ref", MatchEquals="refs/heads/{Branch}"
                    )
                ],
                TargetPipeline=Ref(pipeline),
                TargetAction="BuildSourceAction",
                TargetPipelineVersion=GetAtt(pipeline, "Version"),
                RegisterWithThirdParty=True,
            )
        )
