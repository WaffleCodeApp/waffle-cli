from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    Join,
    Ref,
    iam,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .parameters import Parameters


class Roles:
    sns_role: iam.Role
    user_pool_role: iam.Role

    def __init__(self, t: Template, p: Parameters):
        self.sns_role = t.add_resource(
            iam.Role(
                "AuthSnsRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal(
                                "Service", ["cognito-idp.amazonaws.com"]
                            ),
                        )
                    ]
                ),
                Policies=[
                    iam.Policy(
                        PolicyName=Join(
                            "", [Ref(p.deployment_id), "-AuthMFASnsPolicy"]
                        ),
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": ["sns:Publish"],
                                    "Resource": "*",
                                }
                            ],
                        },
                    )
                ],
            )
        )

        self.user_pool_role = t.add_resource(
            iam.Role(
                "AuthUserPoolRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["lambda.amazonaws.com"]),
                        )
                    ]
                ),
                Policies=[
                    iam.Policy(
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                "-AuthMFAUserPoolPolicy",
                            ],
                        ),
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "lambda:CreateFunction",
                                        "sns:Publish",
                                        "s3:GetObject",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["logs:*"],
                                    "Resource": "arn:aws:logs:*:*:*",
                                },
                            ],
                        },
                    )
                ],
            )
        )
