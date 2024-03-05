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
from .cicd_roles import CicdRoles
from .conditions import Conditions
from .web_bucket import WebBucket
from .artifacts_bucket import ArtifactsBucket


class CodePipeline:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        cr: CicdRoles,
        c: Conditions,
        wb: WebBucket,
        ab: ArtifactsBucket,
    ):
        pipeline: codepipeline.Pipeline = t.add_resource(
            codepipeline.Pipeline(
                "Pipeline",
                DependsOn=["Project"],
                Name=Join("", [Ref(p.deployment_id), "-", Ref(p.pipeline_id)]),
                RoleArn=GetAtt(cr.codepipeline_role, "Arn"),
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
                                    Provider="S3",
                                ),
                                InputArtifacts=[
                                    codepipeline.InputArtifacts(Name="BuildArtifact")
                                ],
                                Configuration={
                                    "BucketName": Ref(wb.bucket),
                                    "Extract": True,
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
