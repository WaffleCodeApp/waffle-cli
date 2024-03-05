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


class CodePipeline:
    def __init__(
        self,
        t: Template,
        p: Parameters,
        c: Conditions,
        ab: ArtifactsBucket,
        cr: CicdRoles,
    ):
        pipeline: codepipeline.Pipeline = t.add_resource(
            codepipeline.Pipeline(
                "Pipeline",
                DependsOn=["Project"],
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
                                "GenerateSharedChangeSet",
                                Name="GenerateSharedChangeSet",
                                ActionTypeId=codepipeline.ActionTypeId(
                                    Category="Deploy",
                                    Owner="AWS",
                                    Version="1",
                                    Provider="CloudFormation",
                                ),
                                InputArtifacts=[
                                    codepipeline.InputArtifacts(Name="BuildArtifact")
                                ],
                                OutputArtifacts=[],
                                Configuration={
                                    "StackName": Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-",
                                            Ref(p.pipeline_id),
                                        ],
                                    ),
                                    "ActionMode": "CHANGE_SET_REPLACE",
                                    "RoleArn": GetAtt(cr.deploy_cfn_role, "Arn"),
                                    "ChangeSetName": Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-",
                                            Ref(p.pipeline_id),
                                            "-changeset",
                                        ],
                                    ),
                                    "Capabilities": "CAPABILITY_NAMED_IAM",
                                    "TemplatePath": "BuildArtifact::cfn-post.yaml",
                                    "TemplateConfiguration": "BuildArtifact::cfn-params.json",
                                    # "ParameterOverrides":
                                },
                                RunOrder=1,
                            ),
                            codepipeline.Actions(
                                "ExecuteChangeset",
                                Name="ExecuteChangeset",
                                ActionTypeId=codepipeline.ActionTypeId(
                                    Category="Deploy",
                                    Owner="AWS",
                                    Version="1",
                                    Provider="CloudFormation",
                                ),
                                Configuration={
                                    "StackName": Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-",
                                            Ref(p.pipeline_id),
                                        ],
                                    ),
                                    "ActionMode": "CHANGE_SET_EXECUTE",
                                    "ChangeSetName": Join(
                                        "",
                                        [
                                            Ref(p.deployment_id),
                                            "-",
                                            Ref(p.pipeline_id),
                                            "-changeset",
                                        ],
                                    ),
                                },
                                InputArtifacts=[],
                                OutputArtifacts=[],
                                RunOrder=2,
                            ),
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
