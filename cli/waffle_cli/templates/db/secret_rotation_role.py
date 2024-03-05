from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    iam,
    Join,
    Ref,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .parameters import Parameters


class SecretRotationRole:
    role: iam.Role

    def __init__(self, t: Template, p: Parameters):
        self.role = t.add_resource(
            iam.Role(
                "CreateSecretRotationLambdaRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["lambda.amazonaws.com"]),
                        )
                    ]
                ),
                Path="/",
                ManagedPolicyArns=[
                    "arn:aws:iam::aws:policy/service-role/"
                    "AWSLambdaVPCAccessExecutionRole",
                    "arn:aws:iam::aws:policy/SecretsManagerReadWrite",
                    "arn:aws:iam::aws:policy/IAMFullAccess",
                ],
                Policies=[
                    iam.Policy(
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                Ref(p.database_id),
                                "-secretrotation",
                            ],
                        ),
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "cloudformation:DescribeStackResources",
                                        "cloudformation:DeleteStack",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "lambda:DeleteFunction",
                                        "lambda:GetFunctionConfiguration",
                                    ],
                                    "Resource": "arn:aws:lambda:*:*:function:SecretsManager*",
                                },
                            ],
                        },
                    )
                ],
            )
        )
