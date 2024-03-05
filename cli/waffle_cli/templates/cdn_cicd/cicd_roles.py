from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    GetAtt,
    Join,
    Ref,
    iam,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .parameters import Parameters
from .artifacts_bucket import ArtifactsBucket
from .web_bucket import WebBucket


class CicdRoles:
    codebuild_role: iam.Role
    codepipeline_role: iam.Role

    def __init__(self, t: Template, p: Parameters, ab: ArtifactsBucket, wb: WebBucket):
        self.codebuild_role = t.add_resource(
            iam.Role(
                "CodeBuildServiceRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["codebuild.amazonaws.com"]),
                        )
                    ]
                ),
                Path="/",
                Policies=[
                    iam.Policy(
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": ["codebuild:*", "iam:PassRole"],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "logs:CreateLogStream",
                                        "logs:FilterLogEvents",
                                        "logs:GetLogEvents",
                                        "logs:PutLogEvents",
                                        "logs:DescribeLogGroups",
                                        "logs:DescribeLogStreams",
                                        "logs:PutRetentionPolicy",
                                        "logs:PutMetricFilter",
                                        "logs:CreateLogGroup",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:CreateBucket",
                                        "s3:GetObject",
                                        "s3:List*",
                                        "s3:PutObject",
                                    ],
                                    "Resource": [
                                        Join(
                                            "",
                                            [
                                                "arn:aws:s3:::",
                                                Ref(ab.artifacts_bucket),
                                            ],
                                        ),
                                        Join(
                                            "",
                                            [
                                                "arn:aws:s3:::",
                                                Ref(ab.artifacts_bucket),
                                                "/*",
                                            ],
                                        ),
                                    ],
                                },
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                                "-CodeBuildService",
                            ],
                        ),
                    )
                ],
            )
        )

        self.codepipeline_role = t.add_resource(
            iam.Role(
                "CodePipelineServiceRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["codepipeline.amazonaws.com"]
                            ),
                        )
                    ]
                ),
                Path="/",
                Policies=[
                    iam.Policy(
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                # {
                                #     "Effect": "Allow",
                                #     "Action": [
                                #         "codecommit:CancelUploadArchive",
                                #         "codecommit:GetBranch",
                                #         "codecommit:GetCommit",
                                #         "codecommit:GetUploadArchiveStatus",
                                #         "codecommit:UploadArchive",
                                #     ],
                                #     "Resource": "*",
                                # },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "codedeploy:CreateDeployment",
                                        "codedeploy:GetApplicationRevision",
                                        "codedeploy:GetDeployment",
                                        "codedeploy:GetDeploymentConfig",
                                        "codedeploy:RegisterApplicationRevision",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "codebuild:BatchGetBuilds",
                                        "codebuild:StartBuild",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "lambda:InvokeFunction",
                                        "lambda:ListFunctions",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:GetObject",
                                        "s3:GetObjectVersion",
                                        "s3:GetBucketVersioning*",
                                        "s3:PutObject",
                                    ],
                                    "Resource": [
                                        Join(
                                            "",
                                            [
                                                "arn:aws:s3:::",
                                                Ref(ab.artifacts_bucket),
                                            ],
                                        ),
                                        Join(
                                            "",
                                            [
                                                "arn:aws:s3:::",
                                                Ref(ab.artifacts_bucket),
                                                "/*",
                                            ],
                                        ),
                                        GetAtt(wb.bucket, "Arn"),
                                        Join(
                                            "",
                                            [
                                                GetAtt(wb.bucket, "Arn"),
                                                "/*",
                                            ],
                                        ),
                                    ],
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["iam:PassRole"],
                                    "Resource": "*",
                                },
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                                "-CodePipelineService",
                            ],
                        ),
                    )
                ],
            )
        )
