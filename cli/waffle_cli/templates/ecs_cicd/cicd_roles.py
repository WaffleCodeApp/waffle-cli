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
    execution_role: iam.Role

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
                                        "ecr:GetDownloadUrlForLayer",
                                        "ecr:BatchGetImage",
                                        "ecr:BatchCheckLayerAvailability",
                                        "ecr:PutImage",
                                        "ecr:InitiateLayerUpload",
                                        "ecr:UploadLayerPart",
                                        "ecr:CompleteLayerUpload",
                                        "ecr:GetAuthorizationToken",
                                    ],
                                    "Resource": "*",
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
                                {
                                    "Effect": "Allow",
                                    "Action": ["secretsmanager:GetSecretValue"],
                                    "Resource": [
                                        # TODO: somehow when the secret is accessed by its name
                                        # during codebuild, the ARN of the secret seems to be different
                                        # for some reason.
                                        # codebuild is trying to access this ARN that comes from the secret name:
                                        # arn:aws:secretsmanager:us-east-2:156249644170:secret:postgres-ONwX1u
                                        # while the actual ARN of the secret of that name would be this:
                                        # arn:aws:secretsmanager:us-east-2:156249644170:secret:development-FermCore-DB-YeH6aA
                                        # as a result the following doesn't work:
                                        # Ref(parameters["DBSecretARN"])
                                        "*"
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
                                        "ecs:*",
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
                                        "ecr:GetDownloadUrlForLayer",
                                        "ecr:BatchGetImage",
                                        "ecr:BatchCheckLayerAvailability",
                                        "ecr:PutImage",
                                        "ecr:InitiateLayerUpload",
                                        "ecr:UploadLayerPart",
                                        "ecr:CompleteLayerUpload",
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

        self.execution_role = t.add_resource(
            iam.Role(
                "ExecutionRole",
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/"
                    "AmazonECSTaskExecutionRolePolicy",
                    # Accessing ECR
                    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
                    # Accessing docker images in S3 (belongs to ECR)
                    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                    # TODO: which one is needed?
                    "arn:aws:iam::aws:policy/service-role/AWSTransferLoggingAccess",
                    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
                ],
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["ecs-tasks.amazonaws.com"]),
                        )
                    ]
                ),
                Path="/",
                # Experimentational part:
                # NOTE: checkout https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html
                Policies=[
                    iam.Policy(
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ecr:GetAuthorizationToken",
                                        "ecr:BatchCheckLayerAvailability",  # TODO: restrict to this vpc
                                        "ecr:GetDownloadUrlForLayer",  # TODO: restrict to this vpc
                                        "ecr:BatchGetImage",  # TODO: restrict to this vpc
                                        "logs:CreateLogStream",
                                        "logs:PutLogEvents",
                                    ],
                                    "Resource": "*",
                                }
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-",
                                Ref(p.pipeline_id),
                                "-TaskExecutionRole",
                            ],
                        ),
                    )
                ],
            )
        )

        # NOTE: this doc is related, but very confusing:
        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using-service-linked-roles.html
        # It talks about the AWSServiceRoleForECS service-role of ECS,
        # but examples show that the name of the role to
        # assume is actually AmazonEC2ContainerServiceRole
        # which is never mentioned in this doc.

        # NOTE: might be useful for ECS service and task roles:
        # https://serverfault.com/questions/854413/confused-by-the-role-requirement-of-ecs
        # self.service_role = t.add_resource(iam.Role(
        #  "ServiceRole",
        #  AssumeRolePolicyDocument=Policy(
        #    Statement=[
        #      Statement(
        #        Effect=Allow,
        #        Action=[AssumeRole],
        #        Principal=Principal(
        #          "Service",
        #          ["ecs.amazonaws.com"]
        #        )
        #      )
        #    ]
        #  ),
        #  Path="/",
        #  ManagedPolicyArns=[
        #    "arn:aws:iam::aws:policy"
        #    "/service-role/AmazonEC2ContainerServiceRole"
        #  ]
        # ))
