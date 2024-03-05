from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Join,
    Ref,
    iam,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .parameters import Parameters
from .artifacts_bucket import ArtifactsBucket


class CicdRoles:
    codebuild_role: iam.Role
    codepipeline_role: iam.Role
    deploy_cfn_role: iam.Role
    deploy_cfn_changeset_role: iam.Role

    def __init__(self, t: Template, p: Parameters, ab: ArtifactsBucket):
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
                                    "Action": [
                                        "logs:CreateLogStream",
                                        "logs:PutLogEvents",
                                        "logs:CreateLogGroup",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["s3:*"],
                                    "Resource": [
                                        Join(
                                            "",
                                            ["arn:aws:s3:::", Ref(ab.artifacts_bucket)],
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
                                {
                                    "Effect": "Allow",
                                    "Action": ["cloudformation:*"],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "kms:GenerateDataKey*",
                                        "kms:Encrypt",
                                        "kms:Decrypt",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["sns:SendMessage"],
                                    "Resource": "*",
                                },
                                # {
                                #   "Effect": "Allow",
                                #   "Action": [
                                #     "secretsmanager:GetSecretValue"
                                #   ],
                                #   "Resource": [
                                #     "*"
                                #   ]
                                # },
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
                                    ],
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "codebuild:StartBuild",
                                        "codebuild:BatchGetBuilds",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "cloudwatch:*",
                                        "sns:*",
                                        "cloudformation:*",
                                        "rds:*",
                                        "sqs:*",
                                        "iam:PassRole",
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

        self.deploy_cfn_role = t.add_resource(
            iam.Role(
                "DeployCfnRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["cloudformation.amazonaws.com"]
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
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "iam:CreateRole",
                                        "iam:AttachRolePolicy",
                                        "iam:PutRolePolicy",
                                        "iam:PassRole",
                                        "iam:DetachRolePolicy",
                                        "iam:ListRolePolicies",
                                        "iam:GetRole",
                                        "iam:DeleteRolePolicy",
                                        "iam:UpdateRoleDescription",
                                        "iam:ListRoles",
                                        "iam:DeleteRole",
                                        "iam:GetRolePolicy",
                                        "iam:CreateInstanceProfile",
                                        "iam:AddRoleToInstanceProfile",
                                        "iam:DeleteInstanceProfile",
                                        "iam:GetInstanceProfile",
                                        "iam:ListInstanceProfiles",
                                        "iam:ListInstanceProfilesForRole",
                                        "iam:RemoveRoleFromInstanceProfile",
                                    ],
                                    # NOTE: the idea is to resctrict these to
                                    # the trs.resources that are required for deployment
                                    # but it's impossible to tell what they would be
                                    # it has to be done by denying access by default
                                    # for the other existing trs.resources
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:CreateBucket",
                                        "s3:GetObject",
                                        "s3:List*",
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
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:*",
                                        "lambda:*",
                                        "codedeploy:*",
                                        "ec2:*",
                                        "cloudwatch:PutMetricAlarm",
                                        "cloudwatch:DeleteAlarms",
                                        "route53:*",
                                        "sns:*",
                                        "dynamodb:*",
                                        "sqs:*",
                                        "cloudfront:CreateDistribution",
                                        "cloudfront:UpdateDistribution",
                                        "cloudfront:DeleteDistribution",
                                        "cloudfront:TagResource",
                                        "cloudfront:UntagResource",
                                        # NOTE: probably a subset of trs.resources is sufficient:
                                        # "events:DescribeRule",
                                        # "events:DeleteRule",
                                        # "events:PutRule",
                                        # "events:ListRules",
                                        "events:*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["apigateway:*"],
                                    # TODO: restrict to the one passed as parameter
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "cloudformation:CreateChangeSet",
                                        "cloudformation:ExecuteChangeSet",
                                        "cloudformation:DeleteChangeSet",
                                        "cloudformation:DeleteStack",
                                    ],
                                    # NOTE: sometimes it seems to be /Include
                                    # sometimes /Serverless-2016-10-31
                                    # using *
                                    # "Resource": "arn:aws:cloudformation:us-east-2:"
                                    # "aws:transform/*",
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
                                "-DeployCloudformation",
                            ],
                        ),
                    )
                ],
            )
        )

        self.deploy_cfn_changeset_role = t.add_resource(
            iam.Role(
                "DeployCfnChangeSetRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["codedeploy.amazonaws.com"]
                            ),
                        )
                    ]
                ),
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForLambda"
                ],
            )
        )
