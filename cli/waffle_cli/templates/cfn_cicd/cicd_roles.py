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
from .roles import Roles


class CicdRoles:
    codebuild_role: iam.Role
    codepipeline_role: iam.Role
    deploy_cfn_role: iam.Role
    deploy_cfn_changeset_role: iam.Role

    def __init__(self, t: Template, p: Parameters, ab: ArtifactsBucket, r: Roles):
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
                                "Waffle-CodeBuildService-",
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
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
                    "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForLambda",
                    "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForCloudFormation",
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
                                "Service",
                                [
                                    "cloudformation.amazonaws.com",
                                ],
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
                                        "iam:TagRole",
                                        "tag:TagResources",
                                        "tag:UntagResources",
                                        "tag:GetResources",
                                        "tag:GetTagKeys",
                                        "tag:GetTagValues",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "iam:PassRole",
                                    ],
                                    "Resource": [
                                        GetAtt(r.lambda_execution_role, "Arn"),
                                        GetAtt(self.deploy_cfn_changeset_role, "Arn"),
                                    ],
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
                                        "cloudwatch:*",
                                        "route53:*",
                                        "sns:*",
                                        "dynamodb:*",
                                        "sqs:*",
                                        "events:*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["apigateway:*"],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "cloudformation:*",
                                    ],
                                    "Resource": "*",
                                },
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                "Waffle-DeployCloudformation-",
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
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
                                        # The CodePipelineServiceRole assumes
                                        # the DeployCfnRole and DeployCfnChangeSetRole
                                        # in order to be able to deploy. The following
                                        # is required for that to work:
                                        "iam:PassRole",
                                    ],
                                    "Resource": [
                                        GetAtt(self.deploy_cfn_role, "Arn"),
                                        GetAtt(self.deploy_cfn_changeset_role, "Arn"),
                                    ],
                                },
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                "Waffle-CodePipelineService-",
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                            ],
                        ),
                    )
                ],
            )
        )
