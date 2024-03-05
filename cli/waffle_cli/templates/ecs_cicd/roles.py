from troposphere import (  # pyright: ignore[reportMissingTypeStubs]
    iam,
    If,
    ImportValue,
    Join,
    Ref,
    Template,
)
from awacs.aws import Allow, Statement, Principal, Policy
from awacs.sts import AssumeRole

from .parameters import Parameters
from .conditions import Conditions
from .secret import Secret


class Roles:
    task_role: iam.Role

    def __init__(self, t: Template, p: Parameters, c: Conditions, s: Secret):
        self.task_role = t.add_resource(
            iam.Role(
                "TaskRole",
                AssumeRolePolicyDocument=Policy(
                    Statement=[
                        Statement(
                            Effect=Allow,
                            Action=[AssumeRole],
                            Principal=Principal("Service", ["ecs-tasks.amazonaws.com"]),
                        )
                    ]
                ),
                Policies=[
                    iam.Policy(
                        PolicyDocument={
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "secretsmanager:Describe*",
                                        "secretsmanager:Get*",
                                        "secretsmanager:List*",
                                    ],
                                    # "Resource": Ref(s.secret),
                                    # ServiceSecret, DeploymentSecret, all DBSecrets
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ssm:Get*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "rds:*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ses:*",
                                    ],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        # TODO: only:
                                        #  cognito-idp:AdminCreateUser
                                        #
                                        "cognito-idp:*",
                                    ],
                                    "Resource": If(
                                        c.custom_user_pool_arn,
                                        Ref(p.user_pool_arn),
                                        If(
                                            c.create_userpool_selected,
                                            ImportValue(
                                                Join(
                                                    "",
                                                    [
                                                        Ref(p.deployment_id),
                                                        "-AuthUserPoolArn",
                                                    ],
                                                )
                                            ),
                                            "",
                                        ),
                                    ),
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "secretsmanager:GetSecretValue",
                                        "secretsmanager:UpdateSecret",
                                    ],
                                    # TODO: Ref to specific topic
                                    "Resource": "*",
                                },
                            ],
                        },
                        PolicyName=Join(
                            "",
                            [
                                Ref(p.deployment_id),
                                Ref(p.pipeline_id),
                                "-Task",
                            ],
                        ),
                    )
                ],
                Path="/",
            )
        )
